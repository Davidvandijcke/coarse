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

import hmac
from pathlib import Path

import modal
from fastapi import HTTPException, Request
from pydantic import BaseModel

app = modal.App("coarse-review")

_repo_root = Path(__file__).resolve().parent.parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    # Docling's OCR stack (and a few other PDF/image libs) link against
    # libGL and glib at runtime. debian_slim doesn't ship these, so without
    # them Docling crashes on first import with `libGL.so.1: cannot open
    # shared object file`. That's the offline fallback when the OpenRouter
    # OCR path fails, so it must actually work.
    .apt_install("libgl1", "libglib2.0-0")
    .pip_install(
        # Install deps only (coarse source is baked into image below)
        "litellm>=1.60",
        "instructor>=1.15.1",
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
        "docling>=2.86.0",
        "transformers>=5.4,<6",
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


def _strip_nul_bytes(text: str | None) -> str | None:
    """Remove NUL bytes and literal \\u0000 escapes before a Supabase write.

    Belt-and-suspenders sibling of ``coarse.extraction._strip_nul_bytes``.
    The extraction layer already scrubs at its seam, but the review markdown
    and error messages flow through several LLM-roundtrip transforms after
    that, any of which could theoretically reintroduce a NUL. Postgres text
    columns reject \\x00 and PostgREST's JSON decoder rejects the 6-char
    escape ``\\u0000`` with SQLSTATE 22P05, so re-strip at the boundary.
    Idempotent and cheap; safe on ``None``.
    """
    if not text:
        return text
    return text.replace("\x00", "").replace("\\u0000", "")


def _sanitize_error(msg: str) -> str:
    """Strip potentially sensitive info from error messages."""
    import re

    # Instructor's retry exceptions wrap the real failure in an XML-like
    # envelope whose OUTER tag is </last_exception>, e.g.
    #
    #   <last_exception>
    #   <failed_attempts>
    #     <generation number="1">
    #       <exception>The output is incomplete due to a max_tokens length limit.</exception>
    #       <completion>...</completion>
    #     </generation>
    #   </failed_attempts>
    #   </last_exception>
    #
    # The old "last non-empty line" heuristic picked up the bare closing tag
    # and threw away everything useful — every instructor retry failure in
    # Supabase showed up as the single string "</last_exception>". Prefer the
    # first <exception>...</exception> payload when present.
    inst_match = re.search(r"<exception>\s*(.*?)\s*</exception>", msg, re.DOTALL)
    if inst_match and inst_match.group(1).strip():
        msg = inst_match.group(1).strip()
    else:
        # Strip traceback to final exception line only
        lines = msg.strip().splitlines()
        if len(lines) > 1:
            last = next((line for line in reversed(lines) if line.strip()), msg)
            # If the "last line" is a bare closing XML tag (e.g. </last_exception>
            # without a matching <exception> block, or any other wrapper), fall
            # back to the whole trimmed message so we don't lose everything.
            if re.fullmatch(r"</[A-Za-z_][\w-]*>", last.strip()):
                msg = msg.strip()
            else:
                msg = last

    # OpenRouter keys: sk-or-v1-...
    msg = re.sub(r"sk-or-v1-[a-zA-Z0-9]{20,}", "[key]", msg)
    # Anthropic keys: sk-ant-... (caught by generic sk- below but listed
    # explicitly so the provider coverage is obvious at a glance).
    msg = re.sub(r"sk-ant-[a-zA-Z0-9_-]{20,}", "[key]", msg)
    # Standard OpenAI-style keys: sk-...
    msg = re.sub(r"sk-[a-zA-Z0-9-]{20,}", "[key]", msg)
    # Groq keys: gsk_...
    msg = re.sub(r"gsk_[a-zA-Z0-9_]{20,}", "[key]", msg)
    # Perplexity keys: pplx-...
    msg = re.sub(r"pplx-[a-zA-Z0-9]{20,}", "[key]", msg)
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


def _classify_hosted_key_error(api_key: str | None) -> str | None:
    """Explain when coarse.ink receives a direct-provider key.

    The hosted product always routes through OpenRouter, even when the chosen
    model ID starts with `openai/`, `anthropic/`, and so on. A direct provider
    key therefore fails later as a generic OpenRouter 401 unless we catch the
    obvious prefixes here and tell the user what kind of key the site expects.

    Keep this intentionally conservative: only classify well-known direct
    provider prefixes so unknown future OpenRouter key formats are not rejected.
    """
    cleaned = (api_key or "").strip()
    if not cleaned or cleaned.startswith("sk-or-v1-"):
        return None

    provider = None
    if cleaned.startswith("sk-ant-"):
        provider = "Anthropic"
    elif cleaned.startswith("sk-"):
        provider = "OpenAI"
    elif cleaned.startswith("gsk_"):
        provider = "Groq"
    elif cleaned.startswith("pplx-"):
        provider = "Perplexity"
    elif cleaned.startswith("AIza"):
        provider = "Google"

    if provider is None:
        return None

    return (
        "coarse.ink requires an OpenRouter API key (usually starts with "
        f"sk-or-v1-), even when you pick a {provider} model. The key you "
        f"pasted looks like a direct {provider} key. Get an OpenRouter key "
        "at https://openrouter.ai/keys and resubmit."
    )


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
    if status == 402 or any(
        kw in msg
        for kw in (
            "spend limit",
            "insufficient",
            "quota exceeded",
            "payment required",
            "billing",
            "credits",
            "exceeded your",
        )
    ):
        return (
            "API key spend limit reached. Add credits or raise your "
            "limit on your provider dashboard, then try again."
        )
    if status == 403:
        return (
            "OpenRouter denied this request (HTTP 403). This usually means "
            "your OpenRouter account has no credits, your privacy settings "
            "block the provider for the model you picked, or you haven't "
            "accepted that model's terms. Add credits at "
            "https://openrouter.ai/credits and review your privacy settings "
            "at https://openrouter.ai/settings/privacy, then start a new "
            "review."
        )
    if status == 429:
        return (
            "Rate limited by the API provider. Wait a minute and try again, "
            "or check your rate limits on your provider dashboard."
        )
    # ExtractionError from coarse may already have a user-friendly message
    if type(exc).__name__ == "ExtractionError":
        return str(exc)
    return None


class ReviewRequest(BaseModel):
    job_id: str
    pdf_storage_path: str
    # user_api_key is retained for backward compatibility with any in-flight
    # spawn() payloads created before the review_secrets migration. New
    # submissions write the key to review_secrets instead; _fetch_and_consume_user_key
    # reads it from there so the key never rides through Modal's managed queue.
    user_api_key: str | None = None
    email: str | None = None
    model: str | None = None
    # Optional author-supplied steering notes (#54). Forwarded to the review
    # pipeline, which wraps them in an <author_notes> fence before passing to
    # the overview/section/editorial agents. Default None = no-op, so older
    # in-flight spawn() payloads without this field still deserialize cleanly.
    author_notes: str | None = None


def _fetch_and_consume_user_key(db, job_id: str) -> str | None:
    """Read the user's OpenRouter key from review_secrets and delete the row.

    One-shot: after this returns, the row is gone. Returns None if no row exists
    (which is the normal path when the caller is still using the backward-compat
    spawn() payload — _resolve_user_api_key then falls back to req.user_api_key).

    Never raises. A SELECT or DELETE failure is logged through _sanitize_error
    and the function returns None so the caller's backward-compat path still
    runs.
    """
    try:
        result = (
            db.table("review_secrets")
            .select("user_api_key")
            .eq("review_id", job_id)
            .maybe_single()
            .execute()
        )
    except Exception as exc:
        print(f"[{job_id}] review_secrets SELECT failed: {_sanitize_error(str(exc))}")
        return None

    # Real postgrest `maybe_single()` returns None directly when the row does
    # not exist; some wrappers return a namespace with .data=None. Handle both.
    if result is None or not getattr(result, "data", None):
        return None

    key = result.data.get("user_api_key") if isinstance(result.data, dict) else None
    if not key:
        return None

    # Delete the row immediately so the key doesn't linger in the DB. A failure
    # here is non-fatal — the TTL cleanup cron will sweep stragglers.
    try:
        db.table("review_secrets").delete().eq("review_id", job_id).execute()
    except Exception as exc:
        print(
            f"[{job_id}] review_secrets DELETE failed "
            f"(non-fatal, TTL cron will sweep): {_sanitize_error(str(exc))}"
        )

    return key


def _resolve_user_api_key(db, req: "ReviewRequest", job_id: str) -> str | None:
    """Resolve the user's OpenRouter key from either source, preferring review_secrets.

    Preferred path: `review_secrets` side-table (one-shot read-and-delete via
    `_fetch_and_consume_user_key`). The key never rode through Modal's managed
    queue, which is the point of task 3(a).

    Backward-compat fallback: `req.user_api_key` from the spawn() payload. Still
    honored so any in-flight job spawned before the frontend was updated keeps
    working across the rollout window. After the frontend rollout completes, the
    backward-compat branch is effectively dead and can be removed in a follow-up.

    Returns None if both sources are empty. Caller is responsible for the
    no-key failure path (it surfaces as a 401 from OpenRouter on the first
    LLM call and is handled by the existing _classify_api_error logic).
    """
    # Preferred path first. Any key found here has already been deleted from
    # review_secrets by _fetch_and_consume_user_key.
    fetched = _fetch_and_consume_user_key(db, job_id)
    cleaned = (fetched or "").strip() or None
    if cleaned is not None:
        return cleaned

    # Backward-compat fallback.
    return (req.user_api_key or "").strip() or None


@app.function(
    image=image,
    timeout=7200,
    # 4 GB: large PDFs + Docling's torch/RapidOCR stack can blow past 2 GB when
    # the OpenRouter OCR path fails and we fall through to offline extraction.
    memory=4096,
    max_containers=20,
    # Explicit retries=0: _resolve_user_api_key consumes the review_secrets row
    # on first read, so a retry would find an empty row, fall back to an empty
    # req.user_api_key, and 401 on the first LLM call. If retries are ever
    # needed here, rework the key-resolution path first (e.g., persist the
    # resolved key in OPENROUTER_API_KEY and short-circuit re-reads, or move
    # the DELETE to after-review-success with a longer TTL).
    retries=0,
    secrets=[
        modal.Secret.from_name("coarse-supabase"),
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
    email = req.email
    model = req.model
    # Scrub NUL bytes from author_notes before it enters the prompt pipeline.
    # Not for Postgres (author_notes is never persisted) but because some LLM
    # providers reject NUL in content strings and surface it as an opaque
    # pipeline failure. Same defense as the paper_markdown / result_markdown
    # scrub at the Supabase seam.
    author_notes = _strip_nul_bytes(req.author_notes)

    print(f"[{job_id}] Starting review — pdf={pdf_storage_path} model={model}")

    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    db = create_client(supabase_url, supabase_key)

    site_url = os.environ.get("SITE_URL", "https://coarse.vercel.app")

    # Update status to running
    db.table("reviews").update({"status": "running"}).eq("id", job_id).execute()
    print(f"[{job_id}] Status set to running")

    # Resolve the user's OpenRouter key. Both strip/normalization and the
    # review_secrets-vs-backward-compat precedence live in _resolve_user_api_key.
    # `resolved_user_key` may come from either source, so the name is
    # intentionally source-agnostic.
    original_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip() or None
    resolved_user_key = _resolve_user_api_key(db, req, job_id)
    hosted_key_error = _classify_hosted_key_error(resolved_user_key)
    if hosted_key_error is not None:
        db.table("reviews").update(
            {
                "status": "failed",
                "error_message": hosted_key_error,
            }
        ).eq("id", job_id).execute()
        raise ValueError(hosted_key_error)
    if resolved_user_key:
        os.environ["OPENROUTER_API_KEY"] = resolved_user_key

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

        # Read os.environ directly — the previous version inferred from local
        # variables, which could lie about the actual state reaching litellm
        # if something between env set and pipeline start cleared the var.
        env_or_key = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
        print(
            f"[{job_id}] Import OK — OPENROUTER_API_KEY="
            f"{'set' if env_or_key else 'MISSING'} "
            f"(len={len(env_or_key)})"
        )
        print(f"[{job_id}] Starting pipeline")

        config = CoarseConfig(extraction_qa=True)
        review, markdown, paper_text = review_paper(
            pdf_path,
            model=model,
            skip_cost_gate=True,
            config=config,
            author_notes=author_notes,
        )
        print(f"[{job_id}] Pipeline complete — {len(markdown)} chars")

        duration = int(time.time() - start)

        db.table("reviews").update(
            {
                "status": "done",
                "paper_title": review.title,
                "model": model,
                "domain": review.domain,
                "result_markdown": _strip_nul_bytes(markdown),
                "paper_markdown": _strip_nul_bytes(paper_text.full_markdown),
                "duration_seconds": duration,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", job_id).execute()

        # Delete the PDF from Supabase Storage on success only. Failed reviews
        # keep their PDF so Modal's infrastructure-level retries (or a manual
        # resubmit of the same job_id) can find it. The cleanup_papers cron
        # (.github/workflows/cleanup_papers.yml) sweeps any PDF older than 24h,
        # which is well above the 2-hour Modal review timeout.
        try:
            db.storage.from_("papers").remove([pdf_storage_path])
        except Exception:
            pass  # Non-critical; cleanup cron will sweep it

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
        db.table("reviews").update(
            {
                "status": "failed",
                "error_message": _strip_nul_bytes(error_msg),
                "duration_seconds": duration,
            }
        ).eq("id", job_id).execute()
        raise
    finally:
        # Restore original API key to prevent leaking user keys across container reuses.
        # Clear first, then restore — avoids partial state if restore itself raises.
        os.environ.pop("OPENROUTER_API_KEY", None)
        if original_key is not None:
            os.environ["OPENROUTER_API_KEY"] = original_key

        # Clean up temp file on local disk (always — no retry needs this).
        # NOTE: we intentionally do NOT delete the PDF from Supabase Storage
        # here. On the success path it's deleted above; on failure it stays
        # so the cleanup cron can sweep it at 24h and Modal can retry.
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)


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
    # `hmac.compare_digest` requires same-type non-empty inputs, so keep the
    # truthiness guard before the constant-time compare.
    if not expected or not token or not hmac.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")

    do_review.spawn(req.model_dump())
    return {"status": "accepted", "job_id": req.job_id}


@app.function(image=image, timeout=30)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "coarse-review"}
