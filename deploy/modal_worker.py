"""Modal worker for coarse web reviews.

Deploys a serverless function that runs paper reviews triggered by the web frontend.
The function reads PDFs from Supabase Storage, runs review_paper(), and writes
results back to Supabase.

Deploy:  modal deploy deploy/modal_worker.py
Secrets: Create in Modal dashboard: coarse-openrouter, coarse-mistral,
         coarse-gemini, coarse-supabase, coarse-webhook
"""
from __future__ import annotations

import modal

app = modal.App("coarse-review")

# Container image: Python 3.12 + coarse (without docling — Mistral OCR is always available)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("coarse", "supabase>=2.0")
)


@app.function(
    image=image,
    timeout=600,  # 10 minutes — covers standard + agentic reviews
    memory=512,
    secrets=[
        modal.Secret.from_name("coarse-openrouter"),  # OPENROUTER_API_KEY (our key)
        modal.Secret.from_name("coarse-mistral"),      # MISTRAL_API_KEY
        modal.Secret.from_name("coarse-gemini"),       # GEMINI_API_KEY (extraction QA)
        modal.Secret.from_name("coarse-supabase"),     # SUPABASE_URL, SUPABASE_SERVICE_KEY
        modal.Secret.from_name("coarse-webhook"),      # MODAL_WEBHOOK_SECRET
    ],
)
@modal.web_endpoint(method="POST")
def run_review(job_id: str, pdf_storage_path: str, user_api_key: str | None = None):
    """Run a paper review for a web submission.

    Args:
        job_id: UUID of the review record in Supabase.
        pdf_storage_path: Path to the PDF in Supabase Storage (e.g., "pdfs/{job_id}.pdf").
        user_api_key: User's OpenRouter API key (BYOK tier). If None, uses our key.
    """
    import os
    import tempfile
    import time
    from datetime import datetime, timezone

    from supabase import create_client

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    db = create_client(supabase_url, supabase_key)

    # Update status to running
    db.table("reviews").update({"status": "running"}).eq("id", job_id).execute()

    # If BYOK, temporarily override API key; restore afterward to prevent leaks
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

        config = CoarseConfig(
            use_coding_agents=False,  # standard mode for web v1
            extraction_qa=True,
        )
        review, markdown, _paper_text = review_paper(
            pdf_path, skip_cost_gate=True, config=config
        )

        duration = int(time.time() - start)

        db.table("reviews").update({
            "status": "done",
            "paper_title": review.title,
            "domain": review.domain,
            "taxonomy": review.taxonomy,
            "result_markdown": markdown,
            "result_json": review.model_dump(mode="json"),
            "duration_seconds": duration,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", job_id).execute()

        # Upload markdown result to storage for easy sharing
        db.storage.from_("results").upload(
            f"{job_id}.md",
            markdown.encode("utf-8"),
            {"content-type": "text/markdown"},
        )

    except Exception as e:
        duration = int(time.time() - start)
        db.table("reviews").update({
            "status": "failed",
            "error_message": str(e)[:1000],
            "duration_seconds": duration,
        }).eq("id", job_id).execute()
        raise  # Let Modal log the full traceback
    finally:
        # Restore original API key to prevent leaking BYOK keys across container reuses
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key
        elif "OPENROUTER_API_KEY" in os.environ and user_api_key:
            del os.environ["OPENROUTER_API_KEY"]
        # Clean up temp file
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


@app.function(image=image, timeout=30)
@modal.web_endpoint(method="GET")
def health():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "coarse-review"}
