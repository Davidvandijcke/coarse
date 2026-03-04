"""Tests for coarse.extraction."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.extraction import _estimate_tokens, extract_text
from coarse.types import PaperText


@pytest.fixture
def mock_docling_result():
    """Create a mock Docling conversion result."""
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = (
        "# Test Paper\n\n## Abstract\n\nThis is a test abstract.\n\n"
        "<!-- PAGE BREAK -->\n"
        "## Introduction\n\nHello, this is a test PDF for coarse extraction.\n"
    )
    mock_result = MagicMock()
    mock_result.document = mock_doc
    return mock_result


@pytest.fixture
def minimal_pdf(tmp_path: Path) -> Path:
    """Create a minimal PDF file (just needs to exist for the mock)."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 minimal")
    return pdf_path


def test_extract_text_returns_paper_text(minimal_pdf: Path, mock_docling_result) -> None:
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.return_value = mock_docling_result
        result = extract_text(minimal_pdf, use_cache=False)
    assert isinstance(result, PaperText)
    assert isinstance(result.full_markdown, str)
    assert len(result.full_markdown) > 0
    assert result.token_estimate > 0


def test_extract_text_markdown_from_docling(minimal_pdf: Path, mock_docling_result) -> None:
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.return_value = mock_docling_result
        result = extract_text(minimal_pdf, use_cache=False)
    assert "# Test Paper" in result.full_markdown
    assert "Introduction" in result.full_markdown


def test_extract_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/path/file.pdf")


def test_token_estimate_heuristic() -> None:
    text = "a" * 400
    assert _estimate_tokens(text) == 100

    text2 = "hello world " * 10
    assert _estimate_tokens(text2) == len(text2) // 4


def test_extract_text_caching(minimal_pdf: Path, mock_docling_result) -> None:
    """Extraction result should be cached and reloaded on second call."""
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.return_value = mock_docling_result
        result1 = extract_text(minimal_pdf, use_cache=True)
        # Second call should use cache — converter not called again
        result2 = extract_text(minimal_pdf, use_cache=True)

    assert result1.full_markdown == result2.full_markdown
    # Converter.convert should only be called once
    MockConverter.return_value.convert.assert_called_once()


def test_extract_text_no_cache(minimal_pdf: Path, mock_docling_result) -> None:
    """With use_cache=False, converter is always called."""
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.return_value = mock_docling_result
        extract_text(minimal_pdf, use_cache=False)
        extract_text(minimal_pdf, use_cache=False)

    assert MockConverter.return_value.convert.call_count == 2


def test_extract_text_docling_error(minimal_pdf: Path) -> None:
    """Docling conversion failure raises ValueError."""
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.side_effect = RuntimeError("bad PDF")
        with pytest.raises(ValueError, match="Cannot convert PDF"):
            extract_text(minimal_pdf, use_cache=False)


def test_extract_text_contains_page_break_markers(minimal_pdf: Path, mock_docling_result) -> None:
    """Extracted markdown should contain page break markers from Docling."""
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.return_value = mock_docling_result
        result = extract_text(minimal_pdf, use_cache=False)
    assert "<!-- PAGE BREAK -->" in result.full_markdown


def test_export_called_with_page_break_placeholder(minimal_pdf: Path, mock_docling_result) -> None:
    """Verify export_to_markdown is called with the page_break_placeholder argument."""
    with patch("coarse.extraction.DocumentConverter") as MockConverter:
        MockConverter.return_value.convert.return_value = mock_docling_result
        extract_text(minimal_pdf, use_cache=False)
    mock_docling_result.document.export_to_markdown.assert_called_once_with(
        page_break_placeholder="<!-- PAGE BREAK -->"
    )
