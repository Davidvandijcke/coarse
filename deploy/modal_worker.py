"""Modal worker for coarse web reviews.

Deploys a serverless function that runs paper reviews triggered by the web frontend.
The web endpoint accepts requests and immediately spawns a background worker via
Modal's .spawn(), returning a fast 202 response. The background worker downloads
the PDF, runs the review pipeline, and writes results back to Supabase.

Deploy:  modal deploy deploy/modal_worker.py
Secrets: Create in Modal dashboard:
  coarse-supabase     SUPABASE_URL, SUPABASE_SERVICE_KEY
  coarse-webhook      MODAL_WEBHOOK_SECRET
  coarse-gmail        GMAIL_USER, GMAIL_APP_PASSWORD
"""
from __future__ import annotations

from pathlib import Path

import modal
from fastapi import HTTPException, Request
from pydantic import BaseModel

app = modal.App("coarse-review")

_repo_root = Path(__file__).resolve().parent.parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        # Install deps only (coarse source is baked into image below)
        "litellm>=1.60",
        "instructor>=1.7",
        "pydantic>=2.0",
        "typer>=0.12",
        "rich>=13.0",
        "tomli-w>=1.0",
        "pymupdf>=1.24",
        "python-dotenv>=1.0",
        "supabase>=2.0",
        "requests>=2.31",
        "fastapi[standard]",
        # Multi-format support
        "mammoth>=1.6",
        "markdownify>=0.12",
        "ebooklib>=0.18",
        "docling>=2.0",
    )
    .add_local_dir(_repo_root / "src" / "coarse", remote_path="/root/coarse")
)


def _send_email(to: str, subject: str, html: str) -> None:
    """Send email via Gmail SMTP. No-op if credentials are missing."""
    import os
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not user or not password:
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = f"coarse <{user}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, password)
        server.send_message(msg)


def _sanitize_error(msg: str) -> str:
    """Strip potentially sensitive info from error messages."""
    import re

    # Strip traceback to final exception line only
    lines = msg.strip().splitlines()
    if len(lines) > 1:
        msg = next((line for line in reversed(lines) if line.strip()), msg)

    # OpenRouter keys: sk-or-v1-...
    msg = re.sub(r"sk-or-v1-[a-zA-Z0-9]{20,}", "[key]", msg)
    # Standard OpenAI-style keys: sk-...
    msg = re.sub(r"sk-[a-zA-Z0-9-]{20,}", "[key]", msg)
    # Gemini/Google API keys: AIza...
    msg = re.sub(r"AIza[a-zA-Z0-9_-]{30,}", "[key]", msg)
    # JWTs / Supabase service keys: eyJ...
    msg = re.sub(r"eyJ[a-zA-Z0-9_-]{20,}", "[key]", msg)
    # Bearer tokens
    msg = re.sub(r"Bearer\s+\S+", "Bearer [key]", msg, flags=re.IGNORECASE)
    # URLs (may contain embedded credentials or project refs)
    msg = re.sub(r"https?://[^\s]+", "[url]", msg)
    # File paths
    msg = re.sub(r"/[^\s:]+/[^\s:]+", "[path]", msg)
    # Long alphanumeric tokens (catch-all for remaining keys)
    msg = re.sub(r"[a-zA-Z0-9]{32,}", "[redacted]", msg)
    return msg[:500]


def _classify_api_error(exc: BaseException) -> str | None:
    """Return a clear, user-facing message for common API errors.

    Returns None if the error isn't a recognized API issue (falls back
    to the generic sanitized message).
    """
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    resp = getattr(exc, "response", None)
    if resp is not None and not isinstance(status, int):
        status = getattr(resp, "status_code", None)
    msg = str(exc).lower()

    if status == 401 or "invalid" in msg and "key" in msg or "unauthorized" in msg:
        return "Invalid API key. Check that your key is correct and active."
    if status == 402 or any(kw in msg for kw in (
        "spend limit", "insufficient", "quota exceeded",
        "payment required", "billing", "credits", "exceeded your",
    )):
        return ("API key spend limit reached. Add credits or raise your "
                "limit on your provider dashboard, then try again.")
    if status == 403:
        return "API key does not have access to this model or endpoint."
    if status == 429:
        return ("Rate limited by the API provider. Wait a minute and try again, "
                "or check your rate limits on your provider dashboard.")
    # ExtractionError from coarse may already have a user-friendly message
    if type(exc).__name__ == "ExtractionError":
        return str(exc)
    return None


class ReviewRequest(BaseModel):
    job_id: str
    pdf_storage_path: str
    user_api_key: str | None = None
    email: str | None = None
    model: str | None = None


@app.function(
    image=image,
    timeout=7200,
    memory=2048,
    max_containers=10,
    secrets=[
        modal.Secret.from_name("coarse-supabase"),
        modal.Secret.from_name("coarse-mistral", required_keys=[]),
        modal.Secret.from_name("coarse-gemini", required_keys=[]),
        modal.Secret.from_name("coarse-openrouter", required_keys=[]),
        modal.Secret.from_name("coarse-webhook"),
        modal.Secret.from_name("coarse-gmail"),
    ],
)
def do_review(req_dict: dict):
    """Background worker that runs the actual review pipeline."""
    import os
    import tempfile
    import time
    from datetime import datetime, timezone

    from supabase import create_client

    req = ReviewRequest(**req_dict)
    job_id = req.job_id
    pdf_storage_path = req.pdf_storage_path
    user_api_key = req.user_api_key
    email = req.email
    model = req.model

    print(f"[{job_id}] Starting review — pdf={pdf_storage_path} model={model}")

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    db = create_client(supabase_url, supabase_key)

    site_url = os.environ.get("SITE_URL", "https://coarse.vercel.app")

    # Update status to running
    db.table("reviews").update({"status": "running"}).eq("id", job_id).execute()
    print(f"[{job_id}] Status set to running")

    # Use user's key; restore original afterward to prevent leaks across container reuses
    original_key = os.environ.get("OPENROUTER_API_KEY")
    if user_api_key:
        os.environ["OPENROUTER_API_KEY"] = user_api_key

    # Download file from Supabase Storage
    pdf_bytes = db.storage.from_("papers").download(pdf_storage_path)
    if not pdf_bytes:
        raise ValueError(f"Storage download returned empty for {pdf_storage_path}")
    print(f"[{job_id}] Downloaded file — {len(pdf_bytes)} bytes")

    ext = Path(pdf_storage_path).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(pdf_bytes)
        pdf_path = f.name

    start = time.time()
    try:
        print(f"[{job_id}] Importing coarse...")
        from coarse import review_paper
        from coarse.config import CoarseConfig
        has_or_key = bool(os.environ.get("OPENROUTER_API_KEY"))
        has_mi_key = bool(os.environ.get("MISTRAL_API_KEY"))
        print(f"[{job_id}] Import OK — OPENROUTER_API_KEY={'set' if has_or_key else 'MISSING'}, MISTRAL_API_KEY={'set' if has_mi_key else 'MISSING'}")
        print(f"[{job_id}] Starting pipeline")

        config = CoarseConfig(use_coding_agents=False, extraction_qa=True)
        review, markdown, paper_text = review_paper(
            pdf_path, model=model, skip_cost_gate=True, config=config
        )
        print(f"[{job_id}] Pipeline complete — {len(markdown)} chars")

        duration = int(time.time() - start)

        db.table("reviews").update({
            "status": "done",
            "paper_title": review.title,
            "model": model,
            "domain": review.domain,
            "result_markdown": markdown,
            "paper_markdown": paper_text.full_markdown,
            "duration_seconds": duration,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", job_id).execute()

        # Send completion email
        if email:
            _send_email(
                to=email,
                subject="Your paper review is ready",
                html=(
                    f"<p>Your review is ready.</p>"
                    f'<p><a href="{site_url}/review/{job_id}">View your review →</a></p>'
                    f"<p><strong>Review key:</strong> <code>{job_id}</code><br>"
                    f"Save this key to return to your review later.</p>"
                    f"<p>— coarse</p>"
                ),
            )

    except BaseException as e:
        duration = int(time.time() - start)
        # BaseException catches SystemExit (Modal SIGTERM on timeout) and
        # KeyboardInterrupt, not just Exception subclasses.
        if isinstance(e, SystemExit):
            error_msg = "Review timed out"
        else:
            error_msg = _classify_api_error(e) or _sanitize_error(str(e))
        db.table("reviews").update({
            "status": "failed",
            "error_message": error_msg,
            "duration_seconds": duration,
        }).eq("id", job_id).execute()
        raise
    finally:
        # Restore original API key to prevent leaking user keys across container reuses.
        # Clear first, then restore — avoids partial state if restore itself raises.
        os.environ.pop("OPENROUTER_API_KEY", None)
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key

        # Clean up temp file
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

        # Delete PDF from storage (user's paper, no reason to retain)
        try:
            db.storage.from_("papers").remove([pdf_storage_path])
        except Exception:
            pass  # Non-critical; don't fail the review


@app.function(
    image=image,
    timeout=60,
    secrets=[
        modal.Secret.from_name("coarse-webhook"),
    ],
)
@modal.fastapi_endpoint(method="POST")
def run_review(request: Request, req: ReviewRequest):
    """Accept a review request and spawn the background worker immediately.

    Returns a fast 202 response so the caller (Vercel) doesn't need to hold
    the HTTP connection open for the full 15-50 minute review pipeline.
    """
    import os

    expected = os.environ.get("MODAL_WEBHOOK_SECRET", "")
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not expected or not token or token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

    do_review.spawn(req.model_dump())
    return {"status": "accepted", "job_id": req.job_id}


@app.function(image=image, timeout=30)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "coarse-review"}
