"""PDF extraction for coarse.

Uses Docling for high-quality document conversion: layout analysis, OCR,
LaTeX rendering, and table extraction — all in one pass. The resulting
markdown is the single source of truth for all downstream processing.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from coarse.types import PaperText

logger = logging.getLogger(__name__)


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


def extract_text(pdf_path: str | Path, use_cache: bool = True) -> PaperText:
    """Extract text from a PDF file using Docling.

    Docling handles layout analysis, OCR for scanned pages, LaTeX formula
    conversion, and table extraction. Returns a single high-quality markdown
    string that serves as the single source of truth for all downstream agents.

    Args:
        pdf_path: Path to the PDF file.
        use_cache: If True (default), use cached extraction when available.

    Returns:
        PaperText with full_markdown and token_estimate.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If Docling cannot convert the file.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Try loading from cache first
    if use_cache:
        cached = _load_cache(path)
        if cached is not None:
            return cached

    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(str(path))
        full_markdown = result.document.export_to_markdown(
            page_break_placeholder="<!-- PAGE BREAK -->"
        )
    except Exception as exc:
        raise ValueError(f"Cannot convert PDF: {pdf_path}") from exc

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
