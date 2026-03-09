"""Modal worker for coarse web reviews.

Deploys a serverless function that runs paper reviews triggered by the web frontend.
The function reads PDFs from Supabase Storage, runs review_paper(), writes results
back to Supabase, deletes the PDF, and emails the user when done.

Deploy:  modal deploy deploy/modal_worker.py
Secrets: Create in Modal dashboard:
  coarse-supabase     SUPABASE_URL, SUPABASE_SERVICE_KEY
  coarse-webhook      MODAL_WEBHOOK_SECRET
Optional (add later for email notifications / operator-provided API keys):
  coarse-resend       RESEND_API_KEY, SITE_URL
  coarse-openrouter   OPENROUTER_API_KEY (fallback if no user key provided)
  coarse-mistral      MISTRAL_API_KEY
  coarse-gemini       GEMINI_API_KEY
"""
from __future__ import annotations

from pathlib import Path

import modal

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
        "resend>=0.6",
        "requests>=2.31",
        "fastapi[standard]",
    )
    .add_local_dir(_repo_root / "src" / "coarse", remote_path="/root/coarse")
)


@app.function(
    image=image,
    timeout=600,
    memory=512,
    secrets=[
        modal.Secret.from_name("coarse-supabase"),
        modal.Secret.from_name("coarse-webhook"),
    ],
)
@modal.fastapi_endpoint(method="POST")
def run_review(
    job_id: str,
    pdf_storage_path: str,
    user_api_key: str | None = None,
    email: str | None = None,
):
    """Run a paper review for a web submission.

    Args:
        job_id: UUID of the review record in Supabase.
        pdf_storage_path: Path to the PDF in Supabase Storage (e.g., "{job_id}.pdf").
        user_api_key: User's OpenRouter API key. Required — we don't cover costs.
        email: User's email for completion notification.
    """
    import os
    import tempfile
    import time
    from datetime import datetime, timezone

    import resend
    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    db = create_client(supabase_url, supabase_key)

    resend.api_key = os.environ.get("RESEND_API_KEY", "")
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
            pdf_path, skip_cost_gate=True, config=config
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
        if email and resend.api_key:
            resend.Emails.send({
                "from": "coarse <reviews@coarse.ai>",
                "to": email,
                "subject": "Your paper review is ready",
                "html": (
                    f"<p>Your review is ready.</p>"
                    f'<p><a href="{site_url}/review/{job_id}">View your review →</a></p>'
                    f"<p><strong>Review key:</strong> <code>{job_id}</code><br>"
                    f"Save this key to return to your review later.</p>"
                    f"<p>— coarse</p>"
                ),
            })

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
