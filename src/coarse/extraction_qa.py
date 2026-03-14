"""Post-extraction QA via vision LLM.

Sends sampled PDF page images + their extracted markdown chunks to a vision model
to spot-check extraction quality. Returns corrections as find-replace pairs.
"""
from __future__ import annotations

import base64
import logging
import re
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from coarse.llm import LLMClient
    from coarse.types import PaperText

logger = logging.getLogger(__name__)

PAGE_BREAK_MARKER = "<!-- PAGE BREAK -->"


# ---------------------------------------------------------------------------
# Response models (structured LLM output)
# ---------------------------------------------------------------------------


class PageCorrection(BaseModel):
    """A correction for a specific page's extraction."""

    page_number: int
    original_snippet: str
    corrected_snippet: str
    issue_type: Literal[
        "garbled_math", "missing_content", "dropped_table", "layout_error", "other"
    ]


class ExtractionQAResult(BaseModel):
    """Single-pass QA result: quality assessment + corrections."""

    overall_quality: Literal["good", "acceptable", "poor"]
    corrections: list[PageCorrection] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# PDF page rendering
# ---------------------------------------------------------------------------


def render_pdf_pages(
    pdf_path: Path, pages: list[int], dpi: int = 150
) -> list[tuple[int, str]]:
    """Render specified pages to base64 PNG.

    Args:
        pdf_path: Path to the PDF file.
        pages: 1-indexed page numbers to render.
        dpi: Resolution for rendering.

    Returns:
        List of (page_number, base64_png_string) tuples.
    """
    import fitz

    doc = fitz.open(str(pdf_path))
    results: list[tuple[int, str]] = []
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    for page_num in pages:
        idx = page_num - 1  # fitz uses 0-indexed
        if idx < 0 or idx >= len(doc):
            logger.warning("Page %d out of range (PDF has %d pages), skipping", page_num, len(doc))
            continue
        try:
            pix = doc[idx].get_pixmap(matrix=mat)
            png_bytes = pix.tobytes("png")
            b64 = base64.b64encode(png_bytes).decode("ascii")
            results.append((page_num, b64))
        except Exception:
            logger.warning("Failed to render page %d, skipping", page_num)
    doc.close()
    return results


def _get_page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""
    import fitz

    doc = fitz.open(str(pdf_path))
    count = len(doc)
    doc.close()
    return count


# ---------------------------------------------------------------------------
# Markdown splitting and page selection
# ---------------------------------------------------------------------------


def _split_by_page(markdown: str) -> list[str]:
    """Split markdown on page break markers.

    Returns a 0-indexed list of per-page chunks.  Page *i* (1-indexed)
    corresponds to ``chunks[i - 1]``.
    If no markers present, returns the entire markdown as a single chunk.
    """
    chunks = markdown.split(PAGE_BREAK_MARKER)
    return [c.strip() for c in chunks]


def _select_qa_pages(num_pages: int, page_chunks: list[str]) -> list[int]:
    """Select pages to QA. Adaptive sampling biased toward complex pages.

    Args:
        num_pages: Total number of pages in the PDF.
        page_chunks: Per-page markdown chunks (0-indexed list, page i = chunk i).

    Returns:
        Sorted list of 1-indexed page numbers to check.
    """
    if num_pages <= 5:
        return list(range(1, num_pages + 1))

    # Score each page by complexity (math, tables, short content, garble)
    scored: list[tuple[int, float]] = []
    for i, chunk in enumerate(page_chunks):
        page_num = i + 1
        score = 0.0
        if "glyph[" in chunk or "formula-not-decoded" in chunk:
            score += 3.0  # highest priority: garbled formulas
        if "$$" in chunk or "\\begin{" in chunk:
            score += 2.0
        if chunk.count("|") > 4:
            score += 1.5
        if len(chunk) < 200 and len(chunk) > 0:
            score += 1.0  # suspiciously short
        scored.append((page_num, score))

    # Always include first and last page
    selected = {1, min(num_pages, len(page_chunks))}

    # Add all high-complexity pages
    for page_num, score in scored:
        if score >= 1.5:
            selected.add(page_num)

    # Fill up to ~15 with evenly spaced pages
    max_pages = min(15, num_pages)
    if len(selected) < max_pages:
        step = max(1, num_pages // (max_pages - len(selected) + 1))
        for p in range(1, num_pages + 1, step):
            selected.add(p)
            if len(selected) >= max_pages:
                break

    return sorted(selected)


# ---------------------------------------------------------------------------
# Pre-filter heuristic
# ---------------------------------------------------------------------------

_GARBLED_PATTERN = re.compile(r"[\ufffd\ufffe\uffff]")


def _needs_vision_qa(markdown: str, num_pages: int) -> bool:
    """Heuristic pre-filter: should we run the vision QA?

    Returns True if the extraction looks like it might have issues:
    - Math/LaTeX present (Docling can garble these)
    - Tables present
    - Very short content per page (possible extraction failure)
    - Garbled Unicode characters detected
    """
    if _GARBLED_PATTERN.search(markdown):
        return True

    if "<!-- formula-not-decoded -->" in markdown:
        return True

    # Check for non-printable / control characters (excluding normal whitespace)
    control_count = sum(
        1 for ch in markdown[:5000]
        if unicodedata.category(ch).startswith("C") and ch not in "\n\r\t"
    )
    if control_count > 10:
        return True

    if "$$" in markdown or "\\begin{" in markdown:
        return True

    # Table heuristic: lines with multiple pipes
    if markdown.count("|") > 20:
        return True

    # Short content per page suggests extraction failure
    if num_pages > 0 and len(markdown) / num_pages < 200:
        return True

    return False


# ---------------------------------------------------------------------------
# Message building
# ---------------------------------------------------------------------------


def _build_qa_messages(
    page_chunks: list[tuple[int, str]],
    page_images: list[tuple[int, str]],
) -> list[dict]:
    """Build multimodal messages for the vision LLM.

    Args:
        page_chunks: List of (page_number, markdown_chunk) tuples.
        page_images: List of (page_number, base64_png) tuples.

    Returns:
        Messages list with system + user messages containing interleaved
        text and image_url content blocks.
    """
    from coarse.prompts import EXTRACTION_QA_SYSTEM

    # Build image lookup
    image_map = dict(page_images)

    # User content: interleave text and images
    content_blocks: list[dict] = []
    for page_num, chunk in page_chunks:
        # Text block for this page
        content_blocks.append({
            "type": "text",
            "text": f"## Page {page_num}\n\n**Extracted markdown:**\n```\n{chunk}\n```\n",
        })
        # Image block if available
        if page_num in image_map:
            content_blocks.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_map[page_num]}",
                },
            })

    # Prepend instruction text
    content_blocks.insert(0, {
        "type": "text",
        "text": "Compare each page's extracted markdown against its image. "
                "Report overall_quality and any corrections needed.\n\n",
    })

    return [
        {"role": "system", "content": EXTRACTION_QA_SYSTEM},
        {"role": "user", "content": content_blocks},
    ]


# ---------------------------------------------------------------------------
# Correction application
# ---------------------------------------------------------------------------


def _apply_corrections(markdown: str, corrections: list[PageCorrection]) -> str:
    """Apply find-replace corrections to the markdown.

    Reverts if the result is >20% shorter than the original (safety check).
    """
    if not corrections:
        return markdown

    result = markdown
    applied = 0
    for corr in corrections:
        if not corr.original_snippet or not corr.original_snippet.strip():
            logger.debug("Ignoring empty original_snippet for page %d", corr.page_number)
            continue
        if corr.original_snippet in result:
            result = result.replace(corr.original_snippet, corr.corrected_snippet, 1)
            applied += 1
        else:
            logger.debug(
                "Correction snippet not found in markdown (page %d), skipping",
                corr.page_number,
            )

    # Safety check: revert if result shrank too much
    if len(result) < len(markdown) * 0.8:
        logger.warning(
            "Corrections shrank markdown by >20%% (%d -> %d chars), reverting",
            len(markdown),
            len(result),
        )
        return markdown

    if applied > 0:
        logger.info("Applied %d/%d extraction corrections", applied, len(corrections))

    return result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_extraction_qa(
    pdf_path: Path, paper_text: "PaperText", client: "LLMClient"
) -> "PaperText":
    """Run post-extraction QA on the extracted markdown.

    Sends sampled page images + markdown chunks to a vision LLM. If the model
    returns corrections, applies them. Gracefully returns the original on any error.

    Args:
        pdf_path: Path to the original PDF.
        paper_text: The extracted PaperText to QA.
        client: LLMClient configured with the vision model.

    Returns:
        PaperText, possibly with corrections applied.
    """
    from coarse.config import resolve_api_key

    # Check if vision model API key is available
    model = client._model
    key = resolve_api_key(model)
    if key is None:
        logger.info("No API key for vision model %s, skipping extraction QA", model)
        return paper_text

    # Get page count
    try:
        num_pages = _get_page_count(pdf_path)
    except Exception:
        logger.warning("Failed to open PDF for QA, skipping")
        return paper_text

    # Pre-filter: skip QA for clean text-only papers
    if not _needs_vision_qa(paper_text.full_markdown, num_pages):
        logger.info("Pre-filter: extraction looks clean, skipping vision QA")
        return paper_text

    # Split markdown by page
    page_chunks = _split_by_page(paper_text.full_markdown)

    # Select pages to check
    selected_pages = _select_qa_pages(num_pages, page_chunks)

    # Render selected pages
    try:
        page_images = render_pdf_pages(pdf_path, selected_pages)
    except Exception:
        logger.warning("Failed to render PDF pages for QA, skipping")
        return paper_text

    if not page_images:
        logger.warning("No pages rendered for QA, skipping")
        return paper_text

    # Build chunks for selected pages only
    selected_chunks: list[tuple[int, str]] = []
    for page_num in selected_pages:
        idx = page_num - 1
        if idx < len(page_chunks):
            selected_chunks.append((page_num, page_chunks[idx]))

    # Build multimodal messages and call vision LLM
    messages = _build_qa_messages(selected_chunks, page_images)

    try:
        qa_result: ExtractionQAResult = client.complete(
            messages, ExtractionQAResult, max_tokens=4096, temperature=0.1
        )
    except Exception:
        logger.warning("Extraction QA LLM call failed, returning original")
        return paper_text

    logger.info(
        "Extraction QA: quality=%s, corrections=%d",
        qa_result.overall_quality,
        len(qa_result.corrections),
    )

    if not qa_result.corrections:
        return paper_text

    # Apply corrections
    corrected_markdown = _apply_corrections(
        paper_text.full_markdown, qa_result.corrections
    )

    if corrected_markdown == paper_text.full_markdown:
        return paper_text

    return paper_text.model_copy(
        update={
            "full_markdown": corrected_markdown,
            "token_estimate": len(corrected_markdown) // 4,
        }
    )
