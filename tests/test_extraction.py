"""Tests for coarse.extraction."""
from __future__ import annotations

import base64
from pathlib import Path

import fitz
import pytest

from coarse.extraction import _estimate_tokens, _extract_text_mode, _extract_vision_mode, extract_text
from coarse.types import PaperText


@pytest.fixture
def minimal_pdf(tmp_path: Path) -> Path:
    """Create a minimal one-page PDF with text using fitz."""
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), "Hello, this is a test PDF for coarse extraction.")
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


@pytest.fixture
def two_page_pdf(tmp_path: Path) -> Path:
    """Create a two-page PDF."""
    pdf_path = tmp_path / "two_page.pdf"
    doc = fitz.open()
    for i in range(1, 3):
        page = doc.new_page()
        page.insert_text((72, 100), f"Page {i} content here.")
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_extract_text_returns_paper_text(minimal_pdf: Path) -> None:
    result = extract_text(minimal_pdf)
    assert isinstance(result, PaperText)
    assert isinstance(result.full_markdown, str)
    assert len(result.full_markdown) > 0
    assert len(result.pages) >= 1
    assert result.token_estimate > 0


def test_extract_text_page_count(two_page_pdf: Path) -> None:
    result = extract_text(two_page_pdf)
    assert len(result.pages) == 2


def test_extract_text_mode_no_images(minimal_pdf: Path) -> None:
    result = extract_text(minimal_pdf, vision=False)
    for page in result.pages:
        assert page.image_b64 is None


def test_extract_vision_mode_has_images(minimal_pdf: Path) -> None:
    result = extract_text(minimal_pdf, vision=True)
    for page in result.pages:
        assert page.image_b64 is not None
        assert len(page.image_b64) > 0
        # Should be valid base64
        decoded = base64.b64decode(page.image_b64)
        assert len(decoded) > 0


def test_extract_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/path/file.pdf")


def test_token_estimate_heuristic() -> None:
    text = "a" * 400
    assert _estimate_tokens(text) == 100

    text2 = "hello world " * 10
    assert _estimate_tokens(text2) == len(text2) // 4


def test_extract_text_full_markdown_nonempty(minimal_pdf: Path) -> None:
    result = extract_text(minimal_pdf)
    assert len(result.full_markdown.strip()) > 0


def test_extract_text_mode_internal(minimal_pdf: Path) -> None:
    doc = fitz.open(str(minimal_pdf))
    full_markdown, pages = _extract_text_mode(doc)
    assert isinstance(full_markdown, str)
    assert len(pages) == doc.page_count
    for page in pages:
        assert page.image_b64 is None
    doc.close()


def test_extract_vision_mode_internal(minimal_pdf: Path) -> None:
    doc = fitz.open(str(minimal_pdf))
    full_markdown, pages = _extract_vision_mode(doc)
    assert isinstance(full_markdown, str)
    assert len(pages) == doc.page_count
    for page in pages:
        assert page.image_b64 is not None
    doc.close()
