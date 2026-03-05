"""PDF extraction for coarse.

Primary: Mistral OCR (94% math accuracy, proper LaTeX).
Fallback: Docling (free, offline, but fails on complex formulas).

Priority order:
1. MISTRAL_API_KEY → litellm.ocr() direct
2. OPENROUTER_API_KEY → OpenRouter file-parser plugin (mistral-ocr engine)
3. Docling → local, free, no key needed
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from coarse.types import PaperText

logger = logging.getLogger(__name__)

PAGE_BREAK = "\n\n<!-- PAGE BREAK -->\n\n"


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
    try:
        cache.write_text(
            paper_text.model_dump_json(indent=None),
            encoding="utf-8",
        )
        size_kb = cache.stat().st_size / 1024
        logger.info("Saved extraction cache (%.1f KB) to %s", size_kb, cache.name)
    except Exception:
        logger.warning("Failed to write extraction cache, continuing without cache")


# ---------------------------------------------------------------------------
# Extraction backends
# ---------------------------------------------------------------------------


def _extract_mistral_direct(path: Path) -> str:
    """Extract via Mistral OCR API (requires MISTRAL_API_KEY)."""
    from litellm import ocr

    from coarse.config import resolve_api_key
    from coarse.models import OCR_MODEL

    key = resolve_api_key(OCR_MODEL)
    if not key:
        raise ValueError("No MISTRAL_API_KEY")

    response = ocr(
        model=OCR_MODEL,
        document={"type": "document_url", "document_url": f"file://{path.resolve()}"},
        api_key=key,
    )
    pages = response.pages
    if not pages:
        raise ValueError("Mistral OCR returned no pages")
    return PAGE_BREAK.join(page.markdown for page in pages)


def _extract_mistral_openrouter(path: Path) -> str:
    """Extract via OpenRouter's Mistral OCR file-parser plugin."""
    import base64

    import requests

    from coarse.config import resolve_api_key
    from coarse.models import OPENROUTER_EXTRACTION_MODEL
    from coarse.prompts import OPENROUTER_EXTRACTION_PROMPT

    api_key = resolve_api_key("openrouter/auto")
    if not api_key:
        raise ValueError("No OPENROUTER_API_KEY")

    with open(path, "rb") as f:
        pdf_b64 = base64.b64encode(f.read()).decode()

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_EXTRACTION_MODEL,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": OPENROUTER_EXTRACTION_PROMPT},
                {"type": "file", "file": {
                    "filename": path.name,
                    "file_data": f"data:application/pdf;base64,{pdf_b64}",
                }},
            ]}],
            "plugins": [{"id": "file-parser", "pdf": {"engine": "mistral-ocr"}}],
        },
        timeout=300,
    )
    resp.raise_for_status()
    data = resp.json()

    # Try annotations first (raw OCR output, no model modification)
    annotations = (
        data.get("choices", [{}])[0].get("message", {}).get("annotations", [])
    )
    for ann in annotations:
        if ann.get("type") == "file":
            texts = [
                p["text"]
                for p in ann["file"].get("content", [])
                if p.get("type") == "text"
            ]
            if texts:
                return PAGE_BREAK.join(texts)

    # Fallback: model response (asked to return text verbatim)
    content = data["choices"][0]["message"]["content"]
    if not content:
        raise ValueError("No content from OpenRouter OCR")
    return content


def _extract_docling(path: Path) -> str:
    """Fallback: extract via Docling (free, offline)."""
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(str(path))
    return result.document.export_to_markdown(
        page_break_placeholder="<!-- PAGE BREAK -->"
    )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def extract_text(pdf_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from a PDF file.

    Tries Mistral OCR (direct API, then OpenRouter plugin) for high-quality
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

    # Try loading from cache first
    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    # Priority: Mistral direct → OpenRouter → Docling
    extractors = [
        ("Mistral OCR (direct)", _extract_mistral_direct),
        ("Mistral OCR (OpenRouter)", _extract_mistral_openrouter),
        ("Docling", _extract_docling),
    ]
    full_markdown = None
    for name, fn in extractors:
        try:
            full_markdown = fn(path)
            logger.info("Extracted via %s (%d chars)", name, len(full_markdown))
            break
        except Exception as exc:
            logger.info("%s unavailable: %s", name, exc)

    if full_markdown is None:
        raise ValueError(
            f"Cannot convert PDF (no extraction backend available): {pdf_path}"
        )

    paper_text = PaperText(
        full_markdown=full_markdown,
        token_estimate=_estimate_tokens(full_markdown),
    )

    # Cache for next time
    if use_cache:
        _save_cache(path, paper_text)

    return paper_text


def _estimate_tokens(text: str) -> int:
    """Rough token estimate using the len // 4 heuristic."""
    return len(text) // 4
