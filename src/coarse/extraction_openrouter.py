"""OpenRouter extraction transport, parsing, and error policy."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from coarse.types import ExtractionError

logger = logging.getLogger(__name__)

PAGE_BREAK = "\n\n<!-- PAGE BREAK -->\n\n"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

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

_OCR_RETRY_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
_OCR_MAX_RETRIES = 9
_OCR_BACKOFF_BASE = 2.0
_OCR_MAX_BACKOFF = 32.0
_OCR_LOG_TRUNCATE = 500


def _scrub_secrets(msg: str) -> str:
    """Strip API keys and bearer tokens from an error string."""
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
    """Return a user-facing message if this is a user-actionable API error."""
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
    """Return True when a user-actionable API error should still try fallback."""
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


def _response_was_billed(resp) -> bool:
    """Return True if the response reports non-zero usage/cost."""
    try:
        data = resp.json()
    except (ValueError, AttributeError):
        return False
    if not isinstance(data, dict):
        return False
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return False

    def _positive_number(val: object) -> bool:
        return isinstance(val, (int, float)) and not isinstance(val, bool) and val > 0

    for key in ("total_cost", "cost"):
        if _positive_number(usage.get(key)):
            return True
    if _positive_number(usage.get("total_tokens")):
        return True
    return False


def _body_retry_code(resp) -> int | None:
    """Return a retryable error code if the response body wraps one, else None."""
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
    """POST to OpenRouter with bounded retries on transient failures."""
    import time

    import requests

    def _wait_for(attempt: int) -> float:
        return min(_OCR_BACKOFF_BASE**attempt, _OCR_MAX_BACKOFF)

    last_network_exc: Exception | None = None
    for attempt in range(_OCR_MAX_RETRIES + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            last_network_exc = exc
            if attempt < _OCR_MAX_RETRIES:
                wait = _wait_for(attempt)
                logger.warning(
                    "OpenRouter OCR network error (attempt %d/%d), retrying in %.1fs: %s",
                    attempt + 1,
                    _OCR_MAX_RETRIES + 1,
                    wait,
                    exc,
                )
                time.sleep(wait)
                continue
            raise ExtractionError(
                f"OpenRouter OCR network error after {_OCR_MAX_RETRIES + 1} attempts: {exc}"
            ) from exc

        if resp.status_code in _OCR_RETRY_STATUSES and attempt < _OCR_MAX_RETRIES:
            wait = _wait_for(attempt)
            logger.warning(
                "OpenRouter OCR returned %d (attempt %d/%d), retrying in %.1fs",
                resp.status_code,
                attempt + 1,
                _OCR_MAX_RETRIES + 1,
                wait,
            )
            time.sleep(wait)
            continue

        body_code = _body_retry_code(resp)
        if body_code is not None and attempt < _OCR_MAX_RETRIES:
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
                _OCR_MAX_RETRIES + 1,
                wait,
            )
            time.sleep(wait)
            continue

        return resp

    raise ExtractionError(
        f"OpenRouter OCR retry loop exited unexpectedly (last exc: {last_network_exc})"
    )


def _parse_openrouter_ocr_response(resp: "requests.Response") -> str:  # noqa: F821
    """Parse an OpenRouter OCR response into a single markdown string."""
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

    content = message.get("content")
    if not content or not isinstance(content, str) or not content.strip():
        logger.warning(
            "OpenRouter OCR returned no usable content; message keys=%s",
            sorted(message.keys()),
        )
        raise ExtractionError("OpenRouter OCR returned empty content")
    return content


def _extract_openrouter_file_parser(path: Path, engine: str) -> str:
    """Extract PDF text via OpenRouter's file-parser plugin."""
    import base64

    from coarse.config import resolve_api_key
    from coarse.models import OPENROUTER_EXTRACTION_MODEL
    from coarse.prompts import OPENROUTER_EXTRACTION_PROMPT

    api_key = resolve_api_key("openrouter/auto")
    if not api_key:
        raise ValueError("No OPENROUTER_API_KEY")

    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise ExtractionError(
            f"File too large ({file_size / 1024 / 1024:.0f} MB). "
            f"Maximum supported size is {MAX_FILE_SIZE / 1024 / 1024:.0f} MB."
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


def _extract_mistral_openrouter(path: Path) -> str:
    """Extract via OpenRouter's Mistral OCR file-parser plugin."""
    return _extract_openrouter_file_parser(path, engine="mistral-ocr")


def _extract_pdftext_openrouter(path: Path) -> str:
    """Extract via OpenRouter's native pdf-text file-parser plugin (free)."""
    return _extract_openrouter_file_parser(path, engine="pdf-text")
