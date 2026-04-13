"""Text extraction for coarse.

Supports PDF, TXT, MD, DOCX, TEX/LATEX, HTML, and EPUB.

PDF priority: Mistral OCR via OpenRouter → pdf-text via OpenRouter → Docling (offline).
DOCX/HTML/TEX: Docling (if installed) → lightweight fallback (mammoth/markdownify/regex).
TXT/MD: Direct read. EPUB: ebooklib + markdownify.
"""

from __future__ import annotations

import html
import json
import logging
import os
import re
from pathlib import Path

from coarse.garble import garble_ratio as compute_garble_ratio
from coarse.garble import normalize_ocr_garble
from coarse.types import ExtractionError, PaperText

logger = logging.getLogger(__name__)

PAGE_BREAK = "\n\n<!-- PAGE BREAK -->\n\n"


def _strip_nul_bytes(text: str) -> str:
    """Remove NUL bytes and literal \\u0000 escapes from an extracted string.

    Postgres ``text`` columns reject the NUL byte (\\x00), and PostgREST's JSON
    path also rejects the 6-char escape sequence ``\\u0000`` with SQLSTATE
    22P05 when it tries to decode the insert body. Some OCR backends emit
    NULs on edge-case scanned PDFs, and those failures surface at the very
    end of the review pipeline — after the user has already paid for the
    LLM work — which is the worst possible time to crash. Stripping here
    is cheap, idempotent, and keeps the downstream Supabase write safe.
    """
    if not text:
        return text
    return text.replace("\x00", "").replace("\\u0000", "")


# Secret-scrub patterns used on backend failure strings before they reach
# logger.warning() or the raised ExtractionError. Kept as a small duplicate
# of deploy/modal_worker.py::_sanitize_error — cross-importing between
# src/ and deploy/ would be worse than 10 lines of duplication.
_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer [key]"),
    (re.compile(r"sk-or-v1-[a-zA-Z0-9]{20,}"), "[key]"),
    (re.compile(r"sk-ant-[a-zA-Z0-9_-]{20,}"), "[key]"),
    (re.compile(r"sk-[a-zA-Z0-9-]{20,}"), "[key]"),
    (re.compile(r"gsk_[a-zA-Z0-9_]{20,}"), "[key]"),
    (re.compile(r"pplx-[a-zA-Z0-9]{20,}"), "[key]"),
    (re.compile(r"AIza[a-zA-Z0-9_-]{30,}"), "[key]"),
    (re.compile(r"eyJ[a-zA-Z0-9_-]{20,}"), "[key]"),
)


def _scrub_secrets(msg: str) -> str:
    """Strip API keys and bearer tokens from an error string.

    Applied to backend-failure strings before they are logged or embedded in
    an ExtractionError. Without this, litellm-wrapped exceptions whose
    stringification embeds request headers can surface Authorization
    tokens to CLI users' terminals and logs.
    """
    for pattern, replacement in _SECRET_PATTERNS:
        msg = pattern.sub(replacement, msg)
    return msg


def _get_api_error_status(exc: Exception) -> int | None:
    """Extract HTTP status code from an API error, if present."""
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if isinstance(status, int):
        return status
    resp = getattr(exc, "response", None)
    if resp is not None:
        s = getattr(resp, "status_code", None)
        if isinstance(s, int):
            return s
    return None


def _classify_api_error(exc: Exception) -> str | None:
    """Return a user-facing message if this is a user-actionable API error.

    Returns None if the error is transient or backend-specific (should fall
    through to the next extraction backend).
    """
    status = _get_api_error_status(exc)
    msg = str(exc).lower()

    if status == 401 or ("invalid" in msg and "key" in msg) or "unauthorized" in msg:
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
            "limit in your provider dashboard."
        )
    if status == 403:
        return (
            "OpenRouter denied the PDF extraction request (HTTP 403). This "
            "usually means your OpenRouter account has no credits, your "
            "privacy settings block the provider we use for extraction, or "
            "you haven't accepted that provider's terms. Add credits at "
            "https://openrouter.ai/credits and review your privacy settings "
            "at https://openrouter.ai/settings/privacy, then start a new "
            "review."
        )
    # Don't classify 429 (rate limit) or 5xx here — those are transient.
    return None


def _describe_api_error(exc: Exception) -> str | None:
    """Return a scrubbed one-line summary of the provider response, if any."""
    resp = getattr(exc, "response", None)
    if resp is None:
        return None

    parts: list[str] = []
    status = getattr(resp, "status_code", None)
    if isinstance(status, int):
        parts.append(f"status={status}")

    try:
        body = resp.json()
    except Exception:
        body = None

    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            message = err.get("message")
            code = err.get("code")
            metadata = err.get("metadata")
            if message:
                parts.append(f"message={message}")
            if code is not None:
                parts.append(f"code={code}")
            if metadata:
                parts.append(f"metadata={metadata}")
        elif err is not None:
            parts.append(f"error={err}")
        elif body:
            parts.append(f"body={body}")
    elif body is not None:
        parts.append(f"body={body}")
    else:
        text = getattr(resp, "text", None)
        if text:
            parts.append(f"body={text}")

    if not parts:
        return None
    return _scrub_secrets("; ".join(str(part) for part in parts))[:500]


def _can_fall_through_api_error(
    extractor_name: str,
    exc: Exception,
    api_msg: str | None = None,
) -> bool:
    """Return True when a user-actionable API error should still try fallback.

    Extraction has a meaningful fallback chain: a paid/provider-specific
    OpenRouter failure on one PDF engine can still succeed on a cheaper or
    fully offline backend. Keep 401 as fail-fast, but let 402/403 on
    OpenRouter extraction engines fall through.
    """
    if "OpenRouter" not in extractor_name:
        return False

    status = _get_api_error_status(exc)
    if status in {402, 403}:
        return True

    return api_msg in {
        "API key spend limit reached. Add credits or raise your limit in your provider dashboard.",
        (
            "OpenRouter denied the PDF extraction request (HTTP 403). This usually means "
            "your OpenRouter account has no credits, your privacy settings block the "
            "provider we use for extraction, or you haven't accepted that provider's "
            "terms. Add credits at https://openrouter.ai/credits and review your privacy "
            "settings at https://openrouter.ai/settings/privacy, then start a new review."
        ),
    }


SUPPORTED_EXTENSIONS = frozenset(
    {
        ".pdf",
        ".txt",
        ".md",
        ".tex",
        ".latex",
        ".html",
        ".htm",
        ".docx",
        ".epub",
    }
)


def _cache_path(pdf_path: Path) -> Path:
    """Return the cache file path for a given PDF."""
    return pdf_path.with_suffix(".extraction_cache.json")


def _load_cache(pdf_path: Path) -> PaperText | None:
    """Load cached extraction if it exists and is newer than the PDF."""
    cache = _cache_path(pdf_path)
    if not cache.exists():
        return None
    if cache.stat().st_mtime < pdf_path.stat().st_mtime:
        logger.info("Cache stale (PDF modified since cache), re-extracting")
        return None
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        paper_text = PaperText.model_validate(data)
        logger.info("Loaded extraction cache from %s", cache.name)
        return paper_text
    except Exception:
        logger.warning("Cache corrupt, re-extracting")
        return None


def _save_cache(pdf_path: Path, paper_text: PaperText) -> None:
    """Save extraction result to cache file next to the PDF."""
    cache = _cache_path(pdf_path)
    # Prevent symlink-following writes (attacker could pre-create symlink)
    if cache.is_symlink():
        logger.warning("Cache path %s is a symlink, refusing to write", cache)
        return
    try:
        cache.write_text(
            paper_text.model_dump_json(indent=None),
            encoding="utf-8",
        )
        cache.chmod(0o600)  # restrict to owner-only (contains paper text)
        size_kb = cache.stat().st_size / 1024
        logger.info("Saved extraction cache (%.1f KB) to %s", size_kb, cache.name)
    except Exception:
        logger.warning("Failed to write extraction cache, continuing without cache")


# ---------------------------------------------------------------------------
# Extraction backends
# ---------------------------------------------------------------------------


_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

# Retry config for transient OpenRouter failures. Only applied to idempotent
# POSTs; network errors and these specific HTTP statuses are retried.
_OCR_RETRY_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
_OCR_MAX_RETRIES = 9  # total attempts = 1 + _OCR_MAX_RETRIES (10 total)
_OCR_BACKOFF_BASE = 2.0  # seconds; actual wait = min(base ** attempt, _OCR_MAX_BACKOFF)
_OCR_MAX_BACKOFF = 32.0  # cap per-retry wait so 10 attempts don't blow the timeout budget
# Backoff sequence: 1 + 2 + 4 + 8 + 16 + 32 + 32 + 32 + 32 = 159s max across 9 retries.


def _get_ocr_max_retries() -> int:
    """Return the OCR retry ceiling, honoring the ``COARSE_OCR_MAX_RETRIES``
    env-var override.

    The module-level default (``_OCR_MAX_RETRIES = 9``, i.e. 10 total
    attempts) is calibrated for the full-review path: generous because
    a review is a committed run and a minute or two of Mistral OCR
    backoff is cheap compared to abandoning a 5-minute pipeline. The
    MCP handoff path (``deploy/mcp_server.py::do_extract``) needs the
    opposite calibration: the user is staring at a live spinner, so
    we'd rather fall through to ``pdf-text`` (then Docling) in seconds
    than burn three minutes waiting for Mistral to recover.
    ``do_extract`` sets ``COARSE_OCR_MAX_RETRIES=2`` before calling
    into extraction; production ``do_review`` leaves the env untouched
    and keeps the default.

    Values are clamped at 0 so a malformed env var can't send us into
    negative-range loops.
    """
    raw = os.environ.get("COARSE_OCR_MAX_RETRIES")
    if not raw:
        return _OCR_MAX_RETRIES
    try:
        return max(0, int(raw))
    except ValueError:
        return _OCR_MAX_RETRIES


# Truncate diagnostic log output so a runaway response body doesn't flood logs.
_OCR_LOG_TRUNCATE = 500


def _response_was_billed(resp) -> bool:
    """Return True if the response reports non-zero usage/cost.

    OpenRouter normally reports zero usage when the file-parser plugin fails
    upstream, so retrying an error body is free. This guard protects against
    the edge case where a billed request also returned an error body — without
    it, 10 retries could in principle multiply the user's API cost. If we
    can't parse the response, we assume it wasn't billed (conservative only
    in the sense that we'd rather retry once more than wrongly give up on a
    response that was actually free).
    """
    try:
        data = resp.json()
    except (ValueError, AttributeError):
        return False
    if not isinstance(data, dict):
        return False
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return False

    # bool is a subclass of int in Python — reject it explicitly so a
    # malformed `usage: {"total_cost": true}` can't trip the billing guard
    # on an otherwise-free error response.
    def _positive_number(val: object) -> bool:
        return isinstance(val, (int, float)) and not isinstance(val, bool) and val > 0

    for key in ("total_cost", "cost"):
        if _positive_number(usage.get(key)):
            return True
    if _positive_number(usage.get("total_tokens")):
        return True
    return False


def _body_retry_code(resp) -> int | None:
    """Return a retryable error code if the response body wraps one, else None.

    OpenRouter's plugin layer (including the Mistral OCR file-parser) sometimes
    returns HTTP 200 with an error body like
    ``{"error": {"message": "Timed out parsing tmp.pdf", "code": 504}}``
    when the upstream provider hiccups. Without checking the body, the transport-
    level retry loop would see HTTP 200, return the response as "successful",
    and then the parser would raise ExtractionError and the review would fall
    through to Docling. We want to retry these just like a raw HTTP 504.
    """
    try:
        data = resp.json()
    except (ValueError, AttributeError):
        return None
    if not isinstance(data, dict):
        return None
    err = data.get("error")
    if not isinstance(err, dict):
        return None
    code = err.get("code")
    if isinstance(code, int) and code in _OCR_RETRY_STATUSES:
        return code
    return None


def _post_openrouter_ocr(
    *,
    url: str,
    headers: dict,
    payload: dict,
    timeout: int,
) -> "requests.Response":  # noqa: F821
    """POST to OpenRouter with bounded retries on transient failures.

    Retries on connection errors, read timeouts, and specific 5xx/429/408
    statuses. Does NOT retry on 4xx (except 408, 429) since those are
    user-actionable (bad key, content policy, etc.).

    Raises ExtractionError with context if all attempts fail with network
    errors. Otherwise returns the last Response (caller must still check
    `raise_for_status()` and body).
    """
    import time

    import requests

    def _wait_for(attempt: int) -> float:
        return min(_OCR_BACKOFF_BASE**attempt, _OCR_MAX_BACKOFF)

    # Resolve the retry ceiling once per call so the env var takes effect
    # per-request without restarting the process. Defaults to 9 (10 total
    # attempts) for production do_review; the MCP extract worker sets
    # COARSE_OCR_MAX_RETRIES=2 for fast spinner feedback.
    max_retries = _get_ocr_max_retries()

    last_network_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            # RequestException is the base class for ConnectionError, Timeout,
            # ChunkedEncodingError, ContentDecodingError, SSLError, etc. — all
            # network-layer failures where retry is the right move.
            last_network_exc = exc
            if attempt < max_retries:
                wait = _wait_for(attempt)
                logger.warning(
                    "OpenRouter OCR network error (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1,
                    max_retries + 1,
                    wait,
                    exc,
                )
                time.sleep(wait)
                continue
            raise ExtractionError(
                f"OpenRouter OCR network error after {max_retries + 1} attempts: {exc}"
            ) from exc

        if resp.status_code in _OCR_RETRY_STATUSES and attempt < max_retries:
            wait = _wait_for(attempt)
            logger.warning(
                "OpenRouter OCR returned %d (attempt %d/%d), retrying in %.1fs",
                resp.status_code,
                attempt + 1,
                max_retries + 1,
                wait,
            )
            time.sleep(wait)
            continue

        # HTTP 200 with a retryable error body (e.g. {"error": {"code": 504}}).
        # OpenRouter's plugin layer uses this shape when the upstream provider
        # (Mistral OCR) times out or hiccups. Treat it the same as a raw HTTP
        # status in _OCR_RETRY_STATUSES — but only if usage is zero. A billed
        # error response means the request actually cost money, and retrying
        # would double-charge the user; stop and let the caller fall through
        # to the next extractor.
        body_code = _body_retry_code(resp)
        if body_code is not None and attempt < max_retries:
            if _response_was_billed(resp):
                logger.warning(
                    "OpenRouter OCR returned 200 with body error code %d AND "
                    "non-zero usage — not retrying to avoid double-billing the user",
                    body_code,
                )
                return resp
            wait = _wait_for(attempt)
            logger.warning(
                "OpenRouter OCR returned 200 with body error code %d "
                "(attempt %d/%d), retrying in %.1fs",
                body_code,
                attempt + 1,
                max_retries + 1,
                wait,
            )
            time.sleep(wait)
            continue

        return resp

    # Unreachable: the loop either returns on success or raises on final network error
    raise ExtractionError(  # pragma: no cover
        f"OpenRouter OCR retry loop exited unexpectedly (last exc: {last_network_exc})"
    )


def _parse_openrouter_ocr_response(resp: "requests.Response") -> str:  # noqa: F821
    """Parse an OpenRouter OCR response into a single markdown string.

    Handles several failure modes OpenRouter exposes:
    - HTTP 200 with `{"error": {...}}` (plugin failed mid-request)
    - HTTP 200 with empty `choices`
    - Malformed annotation structure
    - Empty content fallback
    """
    try:
        data = resp.json()
    except ValueError as exc:
        raise ExtractionError(
            f"OpenRouter returned invalid JSON (HTTP {resp.status_code}): {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ExtractionError(
            f"OpenRouter OCR response was not a JSON object: {type(data).__name__}"
        )

    # OpenRouter can return HTTP 200 with an error body (rate limit, plugin
    # failure, content policy, etc.). Surface a clean error instead of
    # crashing on KeyError: 'choices'.
    if "error" in data and not data.get("choices"):
        err = data["error"]
        msg = err.get("message") if isinstance(err, dict) else None
        logger.warning("OpenRouter OCR returned error body: %s", str(err)[:_OCR_LOG_TRUNCATE])
        raise ExtractionError(f"OpenRouter OCR error: {msg or err}")

    choices = data.get("choices")
    if not choices:
        logger.warning(
            "OpenRouter OCR unexpected response (no choices): keys=%s body=%s",
            sorted(data.keys()),
            str(data)[:_OCR_LOG_TRUNCATE],
        )
        raise ExtractionError(
            f"OpenRouter OCR returned no choices (response keys: {sorted(data.keys())})"
        )

    first_choice = choices[0] if isinstance(choices, list) else {}
    message = (first_choice or {}).get("message") or {}

    # Try annotations first (raw OCR output, no model paraphrasing).
    # File-parser's documented response shape (message.annotations):
    #   [{"type": "file", "file": {"content":
    #       [{"type": "text", "text": ...}, ...]}}]
    annotations = message.get("annotations") or []
    for ann in annotations:
        if not isinstance(ann, dict) or ann.get("type") != "file":
            continue
        file_obj = ann.get("file") or {}
        content_items = file_obj.get("content") or []
        texts = [
            item.get("text", "")
            for item in content_items
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
        ]
        if texts:
            return PAGE_BREAK.join(texts)

    # Fallback: model response (the prompt asks for verbatim text when the
    # plugin output is unavailable or the model paraphrased anyway).
    content = message.get("content")
    if not content or not isinstance(content, str) or not content.strip():
        logger.warning(
            "OpenRouter OCR returned no usable content; message keys=%s",
            sorted(message.keys()),
        )
        raise ExtractionError("OpenRouter OCR returned empty content")
    return content


def _extract_openrouter_file_parser(path: Path, engine: str) -> str:
    """Extract PDF text via OpenRouter's file-parser plugin.

    engine:
        "mistral-ocr" — vision-based OCR, best quality for LaTeX/math, paid,
                        known to be flaky (upstream timeouts).
        "pdf-text"    — native embedded-text extraction, free, fast, reliable.
                        Won't work on scanned image-only PDFs.
    """
    import base64

    from coarse.config import resolve_api_key
    from coarse.models import OPENROUTER_EXTRACTION_MODEL
    from coarse.prompts import OPENROUTER_EXTRACTION_PROMPT

    api_key = resolve_api_key("openrouter/auto")
    if not api_key:
        raise ValueError("No OPENROUTER_API_KEY")

    file_size = path.stat().st_size
    if file_size > _MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {_MAX_FILE_SIZE / 1024 / 1024:.0f} MB."
        )

    with open(path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode()

    resp = _post_openrouter_ocr(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        payload={
            "model": OPENROUTER_EXTRACTION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": OPENROUTER_EXTRACTION_PROMPT},
                        {
                            "type": "file",
                            "file": {
                                "filename": path.name,
                                "file_data": f"data:application/pdf;base64,{pdf_b64}",
                            },
                        },
                    ],
                }
            ],
            "plugins": [{"id": "file-parser", "pdf": {"engine": engine}}],
        },
        timeout=300,
    )
    resp.raise_for_status()
    return _parse_openrouter_ocr_response(resp)


_CHUNK_PAGES = 5
_CHUNK_MAX_WORKERS = 6


def _merge_ocr_chunks(chunks: list[str]) -> str:
    """Merge OCR'd chunk outputs into a single clean markdown document.

    Strips Mistral OCR's ``<file name="...">`` / ``</file>`` wrapper tags,
    removes duplicate page breaks at chunk boundaries, and trims leading
    whitespace/breaks so the document starts with real content (title).
    """
    cleaned = []
    for chunk in chunks:
        # Strip <file name="..."> and </file> tags
        text = re.sub(r"<file\s+name=\"[^\"]*\">\s*", "", chunk)
        text = re.sub(r"\s*</file>\s*", "", text)
        # Strip leading/trailing page breaks and whitespace
        text = text.strip()
        while text.startswith(PAGE_BREAK.strip()):
            text = text[len(PAGE_BREAK.strip()) :].strip()
        while text.endswith(PAGE_BREAK.strip()):
            text = text[: -len(PAGE_BREAK.strip())].strip()
        if text:
            cleaned.append(text)

    merged = PAGE_BREAK.join(cleaned)
    # Collapse any runs of multiple page breaks into one
    pb = PAGE_BREAK.strip()
    doubled = f"{pb}\n\n{pb}"
    while doubled in merged:
        merged = merged.replace(doubled, pb)
    return merged


def _extract_mistral_openrouter(path: Path) -> str:
    """Extract via OpenRouter's Mistral OCR, chunked into 5-page PDFs in parallel.

    Splitting the PDF avoids the upstream timeout that killed whole-file
    requests on papers > ~15 pages. Each chunk is small enough (~200-400 KB)
    to complete in 10-15s, and we send up to 6 in parallel. Wall-clock
    time for a 30-page paper: ~15-20s instead of 150s+ (or timeout).
    """
    import base64
    import tempfile
    from concurrent.futures import ThreadPoolExecutor, as_completed

    import pymupdf

    from coarse.config import resolve_api_key
    from coarse.models import OPENROUTER_EXTRACTION_MODEL
    from coarse.prompts import OPENROUTER_EXTRACTION_PROMPT

    api_key = resolve_api_key("openrouter/auto")
    if not api_key:
        raise ValueError("No OPENROUTER_API_KEY")

    try:
        doc = pymupdf.open(str(path))
    except Exception as exc:
        logger.info(
            "PyMuPDF could not open %s for chunked OCR (%s); falling back to whole-file "
            "mistral-ocr",
            path,
            exc,
        )
        return _extract_openrouter_file_parser(path, engine="mistral-ocr")
    n_pages = len(doc)

    if n_pages <= _CHUNK_PAGES:
        doc.close()
        return _extract_openrouter_file_parser(path, engine="mistral-ocr")

    chunks: list[tuple[int, int, str]] = []
    try:
        for start in range(0, n_pages, _CHUNK_PAGES):
            end = min(start + _CHUNK_PAGES, n_pages)
            chunk_doc = pymupdf.open()
            chunk_doc.insert_pdf(doc, from_page=start, to_page=end - 1)
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            chunk_doc.save(tmp.name)
            chunk_doc.close()
            tmp.close()
            chunks.append((start, end, tmp.name))
        doc.close()

        def _ocr_chunk(chunk_info):
            start, end, chunk_path = chunk_info
            with open(chunk_path, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode()
            resp = _post_openrouter_ocr(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                payload={
                    "model": OPENROUTER_EXTRACTION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": OPENROUTER_EXTRACTION_PROMPT},
                                {
                                    "type": "file",
                                    "file": {
                                        "filename": f"chunk_p{start + 1}-{end}.pdf",
                                        "file_data": f"data:application/pdf;base64,{pdf_b64}",
                                    },
                                },
                            ],
                        }
                    ],
                    "plugins": [{"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}],
                },
                timeout=120,
            )
            resp.raise_for_status()
            return start, _parse_openrouter_ocr_response(resp)

        results: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=_CHUNK_MAX_WORKERS) as pool:
            futures = {pool.submit(_ocr_chunk, c): c for c in chunks}
            for future in as_completed(futures):
                start, md = future.result()
                results[start] = md

        return _merge_ocr_chunks([results[s] for s, _, _ in chunks])

    finally:
        for _, _, chunk_path in chunks:
            try:
                os.unlink(chunk_path)
            except OSError:
                pass


def _extract_pdftext_openrouter(path: Path) -> str:
    """Extract via OpenRouter's native pdf-text file-parser plugin (free)."""
    return _extract_openrouter_file_parser(path, engine="pdf-text")


def _extract_docling(path: Path) -> str:
    """Extract via Docling (free, offline). Supports PDF, DOCX, HTML, LaTeX."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(str(path))
    return result.document.export_to_markdown(page_break_placeholder="<!-- PAGE BREAK -->")


# Minimum markdown length (in chars) below which we consider pymupdf4llm's
# output "empty enough to fall through to OCR". Scanned PDFs with no text
# layer tend to return <50 chars (usually just document metadata); real
# academic papers return 10 KB+. The threshold is generous — pymupdf4llm
# is only meant to win on text-bearing PDFs, and anything with a genuinely
# small amount of text (a 1-page abstract, a tiny note) is still much
# longer than 200 chars after markdownization.
_PYMUPDF4LLM_MIN_CHARS = 200


def _extract_pymupdf4llm(path: Path) -> str:
    """Fast pure-Python PDF extraction via pymupdf4llm.

    For text-bearing PDFs — the overwhelming majority of academic papers,
    which come out of LaTeX/Word/Markdown pipelines with real embedded
    text — this returns clean markdown in 1-2 seconds regardless of
    page count, with no network calls, no API key, no model downloads,
    no cold-start cost. It's what OpenAIReview ships as their default
    extraction engine for exactly this reason.

    Raises ``ExtractionError`` when pymupdf4llm returns empty / too-short
    output. That's the scanned / image-only PDF case, which has no text
    layer for pymupdf to extract; the caller's cascade falls through to
    the OCR path (Mistral → pdf-text → Docling) to handle it.

    This extractor is opted in via ``COARSE_EXTRACTION_FAST=1`` in the
    MCP handoff path (``deploy/mcp_server.py::do_extract``); production
    ``do_review`` leaves the env var unset and uses the OCR cascade
    directly, preserving the existing quality tier for the OpenRouter
    web flow.
    """
    try:
        import pymupdf4llm
    except ImportError as exc:
        raise ExtractionError(
            "pymupdf4llm is not installed. Add 'pymupdf4llm' to your "
            "environment (or install coarse-ink[mcp]) to enable the fast "
            "extraction path."
        ) from exc

    # pymupdf4llm 1.27 ships with `pymupdf_layout`, a GNN-based layout
    # analyzer that auto-activates at import time. The layout path runs
    # per-page OCR by default (`use_ocr=True`), which adds ~5-10s per page
    # — totally unusable for the live spinner UX (a 30-page paper takes
    # 150+ seconds even when every page already has clean embedded text).
    # We don't need layout-based table detection here: the downstream
    # structure parser (structure.py) works off heading regex + LLM
    # classification, not table cells. Disable layout mode to fall back
    # to the legacy `pymupdf_rag` extraction path, which is the same
    # text-extraction code that pymupdf4llm 0.x shipped — pure-Python,
    # no OCR, ~10s for a typical paper.
    pymupdf4llm.use_layout(False)

    markdown = pymupdf4llm.to_markdown(str(path))
    if not isinstance(markdown, str):
        raise ExtractionError(
            f"pymupdf4llm.to_markdown returned {type(markdown).__name__}, expected str"
        )
    stripped = markdown.strip()
    if len(stripped) < _PYMUPDF4LLM_MIN_CHARS:
        raise ExtractionError(
            f"pymupdf4llm returned too little text ({len(stripped)} chars). "
            f"This is usually a scanned / image-only PDF with no text layer. "
            f"Falling through to the OCR cascade."
        )
    return markdown


# ---------------------------------------------------------------------------
# Non-PDF extraction backends (lightweight fallbacks)
# ---------------------------------------------------------------------------


def _extract_plaintext(path: Path) -> str:
    """Read a plain text or markdown file as-is."""
    return path.read_text(encoding="utf-8")


# LaTeX heading patterns: \section{...}, \subsection{...}, etc.
_LATEX_HEADING_RE = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\{([^}]*)\}")
_LATEX_HEADING_LEVEL = {
    "section": "#",
    "subsection": "##",
    "subsubsection": "###",
    "paragraph": "####",
}
# Preamble lines to strip (noise for the reviewer)
_LATEX_PREAMBLE_RE = re.compile(
    r"^\\(documentclass|usepackage|title|author|date|maketitle"
    r"|begin\{document\}|end\{document\})\b.*$",
    re.MULTILINE,
)


def _extract_latex_regex(path: Path) -> str:
    """Extract from LaTeX source with heading conversion to markdown.

    Converts \\section{X} → # X, etc. Strips preamble noise.
    Leaves math, environments, and all other content intact.
    """
    text = path.read_text(encoding="utf-8")
    # Strip preamble lines
    text = _LATEX_PREAMBLE_RE.sub("", text)
    # Convert LaTeX headings to markdown headings
    text = _LATEX_HEADING_RE.sub(lambda m: f"{_LATEX_HEADING_LEVEL[m.group(1)]} {m.group(2)}", text)
    # Clean up excessive blank lines from stripping
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_html_markdownify(path: Path) -> str:
    """Convert HTML to markdown via markdownify (lightweight fallback)."""
    try:
        import markdownify
    except ImportError:
        raise ExtractionError(
            "HTML extraction requires markdownify: pip install coarse-ink[formats]"
        )
    html_str = path.read_text(encoding="utf-8")
    return markdownify.markdownify(html_str, heading_style="ATX")


def _extract_docx_mammoth(path: Path) -> str:
    """Convert DOCX to markdown via mammoth (lightweight fallback)."""
    try:
        import mammoth
    except ImportError:
        raise ExtractionError("DOCX extraction requires mammoth: pip install coarse-ink[formats]")
    with open(path, "rb") as f:
        result = mammoth.convert_to_markdown(f)
    return result.value


def _extract_epub(path: Path) -> str:
    """Extract EPUB chapters to markdown via ebooklib + markdownify."""
    try:
        import ebooklib
        import markdownify
        from ebooklib import epub
    except ImportError:
        raise ExtractionError(
            "EPUB extraction requires ebooklib and markdownify: pip install coarse-ink[formats]"
        )
    book = epub.read_epub(str(path))
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        html_content = item.get_content().decode("utf-8", errors="replace")
        md = markdownify.markdownify(html_content, heading_style="ATX")
        md = md.strip()
        if md:
            chapters.append(md)
    if not chapters:
        raise ExtractionError(f"No text content found in EPUB: {path}")
    return "\n\n---\n\n".join(chapters)


# ---------------------------------------------------------------------------
# Garble detection and normalization
# ---------------------------------------------------------------------------


# Mistral OCR glyph[...] artifact → Unicode mapping
_GLYPH_MAP: dict[str, str] = {
    "lscript": "ℓ",
    "epsilon1": "ε",
    "negationslash": "≠",
    "square": "□",
    "element": "∈",
    "arrowright": "→",
    "lessequal": "≤",
    "greaterequal": "≥",
    "infinity": "∞",
    "summation": "Σ",
    "integral": "∫",
    "partialdiff": "∂",
}
_GLYPH_RE = re.compile(r"glyph\[(\w+)\]")


def normalize_mistral_artifacts(text: str) -> str:
    """Normalize Mistral OCR artifacts (glyph[...], /lscript, HTML entities, etc.)."""
    result = text
    result = _GLYPH_RE.sub(lambda m: _GLYPH_MAP.get(m.group(1), m.group(0)), result)
    result = result.replace("/lscript", "ℓ")
    result = result.replace("<!-- formula-not-decoded -->", "")
    result = html.unescape(result)
    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def extract_text(pdf_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from a PDF file.

    Tries Mistral OCR via OpenRouter's file-parser plugin for high-quality
    LaTeX extraction, falling back to Docling for offline use.

    Args:
        pdf_path: Path to the PDF file.
        use_cache: If True (default), use cached extraction when available.

    Returns:
        PaperText with full_markdown and token_estimate.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If no extraction backend can convert the file.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    file_size = path.stat().st_size
    if file_size > _MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {_MAX_FILE_SIZE // 1024 // 1024} MB."
        )

    with open(path, "rb") as f:
        magic = f.read(5)
    if magic != b"%PDF-":
        raise ExtractionError(f"File does not appear to be a PDF: {pdf_path}")

    # Try loading from cache first
    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    # Priority cascade — both modes now use Mistral OCR first since the
    # chunked-parallel implementation keeps wall-clock time under 20-25s
    # even for 50-page papers. pymupdf4llm is the offline fallback when
    # no OpenRouter key is available (CLI usage without an API key).
    # Docling is kept as a last resort for scanned PDFs.
    if os.environ.get("COARSE_EXTRACTION_FAST") == "1":
        extractors = [
            ("Mistral OCR (OpenRouter, chunked)", _extract_mistral_openrouter),
            ("pymupdf4llm", _extract_pymupdf4llm),
            ("pdf-text (OpenRouter)", _extract_pdftext_openrouter),
        ]
    else:
        extractors = [
            ("Mistral OCR (OpenRouter, chunked)", _extract_mistral_openrouter),
            ("pdf-text (OpenRouter)", _extract_pdftext_openrouter),
            ("Docling", _extract_docling),
        ]
    full_markdown = None
    errors: list[str] = []
    for idx, (name, fn) in enumerate(extractors):
        try:
            full_markdown = fn(path)
            logger.info("Extracted via %s (%d chars)", name, len(full_markdown))
            break
        except Exception as exc:
            api_msg = _classify_api_error(exc)
            if api_msg:
                summary = _describe_api_error(exc)
                has_fallback = idx < len(extractors) - 1
                if has_fallback and _can_fall_through_api_error(name, exc, api_msg):
                    errors.append(f"{name}: {api_msg}")
                    if summary:
                        logger.warning(
                            "%s returned a recoverable API denial; trying fallback backend. %s",
                            name,
                            summary,
                        )
                    else:
                        logger.warning(
                            "%s returned a recoverable API denial; trying fallback backend: %s",
                            name,
                            api_msg,
                        )
                    continue
                if summary:
                    logger.warning("%s failed with API error: %s", name, summary)
                raise ExtractionError(api_msg) from exc
            scrubbed = _scrub_secrets(str(exc))
            errors.append(f"{name}: {scrubbed}")
            logger.warning("%s failed: %s", name, scrubbed)

    if full_markdown is None:
        detail = _scrub_secrets("; ".join(errors))
        raise ExtractionError(f"Cannot convert PDF: all extraction backends failed. {detail}")

    # Normalize Mistral OCR artifacts unconditionally
    full_markdown = normalize_mistral_artifacts(full_markdown)

    # Strip NUL bytes before anything downstream touches the text. See
    # _strip_nul_bytes for the full rationale — short version: Postgres 22P05.
    full_markdown = _strip_nul_bytes(full_markdown)

    # Detect and normalize OCR garble from older PDFs
    garble = compute_garble_ratio(full_markdown)
    if garble > 0.001:
        logger.info("Garble ratio %.4f detected, applying OCR normalization", garble)
        full_markdown = normalize_ocr_garble(full_markdown)
        garble = compute_garble_ratio(full_markdown)  # recompute after normalization

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
        garble_ratio=garble,
    )

    # Cache for next time
    if use_cache:
        _save_cache(path, paper_text)

    return paper_text


def _estimate_tokens(text: str) -> int:
    """Rough token estimate using the len // 4 heuristic."""
    return len(text) // 4


# ---------------------------------------------------------------------------
# Multi-format entry point
# ---------------------------------------------------------------------------

# Formats where Docling gives best quality (try first, fall back to lightweight)
_DOCLING_FORMATS = frozenset({".docx", ".html", ".htm", ".tex", ".latex"})
_FALLBACKS = {
    ".docx": _extract_docx_mammoth,
    ".html": _extract_html_markdownify,
    ".htm": _extract_html_markdownify,
    ".tex": _extract_latex_regex,
    ".latex": _extract_latex_regex,
}


def extract_file(file_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from any supported file format.

    For PDFs: Mistral OCR (direct) → OpenRouter → Docling.
    For DOCX/HTML/TEX: Docling (if installed) → lightweight fallback.
    For TXT/MD: direct read. For EPUB: ebooklib + markdownify.

    Args:
        file_path: Path to the file.
        use_cache: If True (default), use cached extraction when available.

    Returns:
        PaperText with full_markdown and token_estimate.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size = path.stat().st_size
    if file_size > _MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {_MAX_FILE_SIZE // 1024 // 1024} MB."
        )

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ExtractionError(
            f"Unsupported file format: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # PDFs: existing Mistral OCR → OpenRouter → Docling pipeline
    if ext == ".pdf":
        return extract_text(path, use_cache=use_cache)

    # Non-PDF: cache check
    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    # Formats where Docling gives best quality
    if ext in _DOCLING_FORMATS:
        try:
            full_markdown = _extract_docling(path)
            logger.info("Extracted %s via Docling (%d chars)", ext, len(full_markdown))
        except Exception as exc:
            logger.info("Docling unavailable for %s: %s, using fallback", ext, exc)
            full_markdown = _FALLBACKS[ext](path)
    elif ext == ".epub":
        full_markdown = _extract_epub(path)
    else:  # .txt, .md
        full_markdown = _extract_plaintext(path)

    # Same NUL-strip as the PDF path — non-PDF extractors can also carry
    # NULs (malformed TXT, Word docs with embedded binary).
    full_markdown = _strip_nul_bytes(full_markdown)

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
        garble_ratio=0.0,
    )
    if use_cache:
        _save_cache(path, paper_text)
    return paper_text
