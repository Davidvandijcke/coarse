"""PDF extraction for coarse.

Converts a PDF file to PaperText using pymupdf4llm (text mode) or
pymupdf page rendering (vision mode).
"""
from __future__ import annotations

import base64
from pathlib import Path

import fitz  # pymupdf
import pymupdf4llm

from coarse.types import PageContent, PaperText


def extract_text(pdf_path: str | Path, vision: bool = False) -> PaperText:
    """Extract text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.
        vision: If True, render pages as images instead of extracting text.

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


def _extract_vision_mode(doc: fitz.Document) -> tuple[str, list[PageContent]]:
    """Render pages as PNG images and base64-encode them.

    Returns:
        Tuple of (full_markdown placeholder, pages with image_b64 set).
    """
    pages = []
    page_texts = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        page_texts.append(text)
        pixmap = page.get_pixmap(dpi=150)
        png_bytes = pixmap.tobytes("png")
        image_b64 = base64.b64encode(png_bytes).decode("utf-8")
        pages.append(PageContent(page_num=page_num, text=text, image_b64=image_b64))
    full_markdown = "\n\n".join(page_texts)
    return full_markdown, pages


def _estimate_tokens(text: str) -> int:
    """Rough token estimate using the len // 4 heuristic."""
    return len(text) // 4
