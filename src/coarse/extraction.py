"""PDF extraction for coarse.

Converts a PDF file to PaperText using pymupdf4llm (text mode) or
pymupdf page rendering (vision mode).
"""
from __future__ import annotations

import base64
import logging
from pathlib import Path

import fitz  # pymupdf
import pymupdf4llm

from coarse.types import PageContent, PaperText

logger = logging.getLogger(__name__)

# Pages with more vector drawings than this are considered "figure pages"
# and get rendered as images in vision mode.
_VECTOR_DRAWING_THRESHOLD = 50


def extract_text(pdf_path: str | Path, vision: bool = False) -> PaperText:
    """Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.
        vision: If True, render figure pages as images for multimodal input.

    Returns:
        PaperText with full_markdown, per-page PageContent list, and token_estimate.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If pymupdf cannot open the file (encrypted/corrupt).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        raise ValueError(f"Cannot open PDF: {pdf_path}") from exc

    if vision:
        full_markdown, pages = _extract_vision_mode(doc)
    else:
        full_markdown, pages = _extract_text_mode(doc)

    return PaperText(
        full_markdown=full_markdown,
        pages=pages,
        token_estimate=_estimate_tokens(full_markdown),
    )


def _extract_text_mode(doc: fitz.Document) -> tuple[str, list[PageContent]]:
    """Extract text using pymupdf4llm for full markdown and fitz for per-page text.

    Returns:
        Tuple of (full_markdown, pages).
    """
    full_markdown = pymupdf4llm.to_markdown(doc)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append(PageContent(page_num=page_num, text=text))
    return full_markdown, pages


def _page_has_figures(page: fitz.Page) -> bool:
    """Detect whether a page contains figures/charts worth rendering as images.

    Checks for raster images (embedded PNGs/JPEGs) and high vector drawing
    counts (plots/charts rendered as paths). Tables and equations are handled
    better by text extraction, so they don't trigger image rendering.
    """
    if page.get_images(full=True):
        return True
    if len(page.get_drawings()) > _VECTOR_DRAWING_THRESHOLD:
        return True
    return False


def _extract_vision_mode(doc: fitz.Document) -> tuple[str, list[PageContent]]:
    """Extract text + selectively render figure pages as images.

    Uses pymupdf4llm for full_markdown (same quality as text mode).
    Only pages with actual figures/charts get rendered as images —
    text-only and equation-only pages stay as text.
    """
    full_markdown = pymupdf4llm.to_markdown(doc)
    pages = []
    figure_count = 0
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        image_b64 = None
        if _page_has_figures(page):
            pixmap = page.get_pixmap(dpi=150)
            png_bytes = pixmap.tobytes("png")
            image_b64 = base64.b64encode(png_bytes).decode("utf-8")
            figure_count += 1
        pages.append(PageContent(page_num=page_num, text=text, image_b64=image_b64))
    logger.info("Vision mode: %d/%d pages have figures", figure_count, len(doc))
    return full_markdown, pages


def _estimate_tokens(text: str) -> int:
    """Rough token estimate using the len // 4 heuristic."""
    return len(text) // 4
