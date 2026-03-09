"""Modal worker for coarse web reviews.

Deploys a serverless function that runs paper reviews triggered by the web frontend.
The function reads PDFs from Supabase Storage, runs review_paper(), writes results
back to Supabase, deletes the PDF, and emails the user when done.

Deploy:  modal deploy deploy/modal_worker.py
Secrets: Create in Modal dashboard:
  coarse-supabase     SUPABASE_URL, SUPABASE_SERVICE_KEY
  coarse-webhook      MODAL_WEBHOOK_SECRET
  coarse-gmail        GMAIL_USER, GMAIL_APP_PASSWORD
"""
from __future__ import annotations

from pathlib import Path

import modal
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


class ReviewRequest(BaseModel):
    job_id: str
    pdf_storage_path: str
    user_api_key: str | None = None
    email: str | None = None
    model: str | None = None


@app.function(
    image=image,
    timeout=600,
    memory=512,
    secrets=[
        modal.Secret.from_name("coarse-supabase"),
        modal.Secret.from_name("coarse-webhook"),
        modal.Secret.from_name("coarse-gmail"),
    ],
)
@modal.fastapi_endpoint(method="POST")
def run_review(req: ReviewRequest):
    """Run a paper review for a web submission."""
    import os
    import tempfile
    import time
    from datetime import datetime, timezone

    from supabase import create_client

    job_id = req.job_id
    pdf_storage_path = req.pdf_storage_path
    user_api_key = req.user_api_key
    email = req.email
    model = req.model

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    db = create_client(supabase_url, supabase_key)

    site_url = os.environ.get("SITE_URL", "https://coarse.ai")

    # Update status to running
    db.table("reviews").update({"status": "running"}).eq("id", job_id).execute()

    # Use user's key; restore original afterward to prevent leaks across container reuses
    original_key = os.environ.get("OPENROUTER_API_KEY")
    if user_api_key:
        os.environ["OPENROUTER_API_KEY"] = user_api_key

    # Download PDF from Supabase Storage
    pdf_bytes = db.storage.from_("papers").download(pdf_storage_path)
    if not pdf_bytes:
        raise ValueError(f"Storage download returned empty for {pdf_storage_path}")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(pdf_bytes)
        pdf_path = f.name

    start = time.time()
    try:
        from coarse import review_paper
        from coarse.config import CoarseConfig

        config = CoarseConfig(use_coding_agents=False, extraction_qa=True)
        review, markdown, _paper_text = review_paper(
            pdf_path, model=model, skip_cost_gate=True, config=config
        )

        duration = int(time.time() - start)

        db.table("reviews").update({
            "status": "done",
            "paper_title": review.title,
            "domain": review.domain,
            "result_markdown": markdown,
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

    except Exception as e:
        duration = int(time.time() - start)
        db.table("reviews").update({
            "status": "failed",
            "error_message": str(e)[:1000],
            "duration_seconds": duration,
        }).eq("id", job_id).execute()
        raise
    finally:
        # Restore original API key to prevent leaking user keys across container reuses
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key
        elif "OPENROUTER_API_KEY" in os.environ and user_api_key:
            del os.environ["OPENROUTER_API_KEY"]

        # Clean up temp file
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

        # Delete PDF from storage (user's paper, no reason to retain)
        try:
            db.storage.from_("papers").remove([pdf_storage_path])
        except Exception:
            pass  # Non-critical; don't fail the review


@app.function(image=image, timeout=30)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "coarse-review"}
