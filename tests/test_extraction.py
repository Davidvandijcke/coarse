"""Tests for coarse.extraction."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from coarse.extraction import _estimate_tokens, extract_text
from coarse.types import PaperText


def _mock_ocr_response(pages_markdown: list[str]):
    """Create a mock litellm.ocr() response with pages."""
    pages = [SimpleNamespace(markdown=md) for md in pages_markdown]
    return SimpleNamespace(pages=pages)


@pytest.fixture
def mock_ocr_pages():
    """Sample OCR page markdowns."""
    return [
        "# Test Paper\n\n## Abstract\n\nThis is a test abstract.",
        "## Introduction\n\nHello, this is a test PDF for coarse extraction.",
    ]


@pytest.fixture
def minimal_pdf(tmp_path: Path) -> Path:
    """Create a minimal PDF file (just needs to exist for the mock)."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 minimal")
    return pdf_path


def test_extract_text_returns_paper_text(minimal_pdf: Path, mock_ocr_pages) -> None:
    with patch("litellm.ocr", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_text(minimal_pdf, use_cache=False)
    assert isinstance(result, PaperText)
    assert isinstance(result.full_markdown, str)
    assert len(result.full_markdown) > 0
    assert result.token_estimate > 0


def test_extract_text_contains_page_breaks(minimal_pdf: Path, mock_ocr_pages) -> None:
    with patch("litellm.ocr", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "<!-- PAGE BREAK -->" in result.full_markdown
    assert "# Test Paper" in result.full_markdown
    assert "Introduction" in result.full_markdown


def test_extract_text_joins_pages_with_page_break(minimal_pdf: Path) -> None:
    pages = ["Page 1 content", "Page 2 content", "Page 3 content"]
    with patch("litellm.ocr", return_value=_mock_ocr_response(pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_text(minimal_pdf, use_cache=False)
    assert result.full_markdown.count("<!-- PAGE BREAK -->") == 2


def test_extract_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/path/file.pdf")


def test_token_estimate_heuristic() -> None:
    text = "a" * 400
    assert _estimate_tokens(text) == 100

    text2 = "hello world " * 10
    assert _estimate_tokens(text2) == len(text2) // 4


def test_extract_text_caching(minimal_pdf: Path, mock_ocr_pages) -> None:
    """Extraction result should be cached and reloaded on second call."""
    mock_fn = MagicMock(return_value=_mock_ocr_response(mock_ocr_pages))
    with patch("litellm.ocr", mock_fn):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result1 = extract_text(minimal_pdf, use_cache=True)
            # Second call should use cache — ocr not called again
            result2 = extract_text(minimal_pdf, use_cache=True)

    assert result1.full_markdown == result2.full_markdown
    mock_fn.assert_called_once()


def test_extract_text_no_cache(minimal_pdf: Path, mock_ocr_pages) -> None:
    """With use_cache=False, OCR is always called."""
    mock_fn = MagicMock(return_value=_mock_ocr_response(mock_ocr_pages))
    with patch("litellm.ocr", mock_fn):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            extract_text(minimal_pdf, use_cache=False)
            extract_text(minimal_pdf, use_cache=False)

    assert mock_fn.call_count == 2


def test_fallback_to_docling(minimal_pdf: Path) -> None:
    """When Mistral OCR is unavailable, should fall back to Docling."""
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "# Docling Fallback\n\nContent here."
    mock_result = MagicMock()
    mock_result.document = mock_doc

    with patch("coarse.config.resolve_api_key", return_value=None):
        with patch("docling.document_converter.DocumentConverter") as MockConverter:
            MockConverter.return_value.convert.return_value = mock_result
            result = extract_text(minimal_pdf, use_cache=False)

    assert "Docling Fallback" in result.full_markdown


def test_all_backends_fail(minimal_pdf: Path) -> None:
    """When all backends fail, raises ValueError."""
    with patch("coarse.config.resolve_api_key", return_value=None):
        with patch(
            "docling.document_converter.DocumentConverter",
            side_effect=ImportError("no docling"),
        ):
            with pytest.raises(ValueError, match="no extraction backend"):
                extract_text(minimal_pdf, use_cache=False)
