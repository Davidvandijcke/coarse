"""Tests for coarse.extraction_qa — post-extraction QA via vision LLM."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from coarse.extraction_qa import (
    ExtractionQAResult,
    PageCorrection,
    _apply_corrections,
    _build_qa_messages,
    _needs_vision_qa,
    _select_qa_pages,
    _split_by_page,
)
from coarse.models import VISION_MODEL
from coarse.types import PaperText

# ---------------------------------------------------------------------------
# Unit tests: _split_by_page
# ---------------------------------------------------------------------------


def test_split_by_page_basic():
    md = "Page one content\n<!-- PAGE BREAK -->\nPage two\n<!-- PAGE BREAK -->\nPage three"
    chunks = _split_by_page(md)
    assert len(chunks) == 3
    assert chunks[0] == "Page one content"
    assert chunks[1] == "Page two"
    assert chunks[2] == "Page three"


def test_split_by_page_no_markers():
    md = "Just some text with no page breaks at all."
    chunks = _split_by_page(md)
    assert len(chunks) == 1
    assert chunks[0] == md


# ---------------------------------------------------------------------------
# Unit tests: _needs_vision_qa
# ---------------------------------------------------------------------------


def test_needs_vision_qa_math():
    md = "Some text with $$x^2 + y^2 = z^2$$ inline."
    assert _needs_vision_qa(md, 5) is True


def test_needs_vision_qa_latex_begin():
    md = "Text with \\begin{equation} stuff \\end{equation}"
    assert _needs_vision_qa(md, 5) is True


def test_needs_vision_qa_clean_text():
    md = "This is a clean social science paper with no math or tables. " * 50
    assert _needs_vision_qa(md, 5) is False


def test_needs_vision_qa_short_pages():
    md = "Very short."
    assert _needs_vision_qa(md, 10) is True  # 11 chars / 10 pages < 200


def test_needs_vision_qa_tables():
    md = "| col1 | col2 | col3 |\n" * 10
    assert _needs_vision_qa(md, 3) is True


def test_needs_vision_qa_garbled_unicode():
    md = "Normal text \ufffd\ufffd garbled stuff"
    assert _needs_vision_qa(md, 5) is True


# ---------------------------------------------------------------------------
# Unit tests: _select_qa_pages
# ---------------------------------------------------------------------------


def test_select_qa_pages_small_pdf():
    chunks = ["chunk"] * 3
    result = _select_qa_pages(3, chunks)
    assert result == [1, 2, 3]


def test_select_qa_pages_five_pages():
    chunks = ["chunk"] * 5
    result = _select_qa_pages(5, chunks)
    assert result == [1, 2, 3, 4, 5]


def test_select_qa_pages_large_pdf():
    # 30 pages, some with math
    chunks = ["plain text content here"] * 30
    chunks[5] = "Here is $$x^2$$ math"
    chunks[12] = "A table | col1 | col2 | col3 | col4 |"
    chunks[20] = "More \\begin{equation} latex \\end{equation}"
    result = _select_qa_pages(30, chunks)
    # Should include page 1 (first), page 30 (last), and math/table pages
    assert 1 in result
    assert 30 in result
    assert 6 in result  # chunks[5] has math → page 6
    assert 21 in result  # chunks[20] has latex → page 21
    assert len(result) <= 15


def test_select_qa_pages_clamps_to_num_pages():
    """Mistral OCR sometimes emits an extra trailing chunk (e.g. 57 chunks for
    a 56-page PDF). _select_qa_pages must never return a page number greater
    than num_pages, otherwise render_pdf_pages logs 'Page N out of range'."""
    # 56-page PDF with 57 chunks; last chunk has high-complexity markers that
    # would otherwise score into the selected set.
    chunks = ["plain text content here"] * 56 + [
        "See glyph[lscript] and \\begin{equation} trailing \\end{equation}"
    ]
    result = _select_qa_pages(56, chunks)
    assert max(result) <= 56
    assert 57 not in result


def test_select_qa_pages_garbled_formula_pages_prioritized():
    """Pages with glyph[...] or formula-not-decoded should always be selected."""
    chunks = ["plain text content here"] * 20
    chunks[3] = "See glyph[lscript] and glyph[epsilon1] in this formula"
    chunks[15] = "The result is <!-- formula-not-decoded --> which simplifies"
    result = _select_qa_pages(20, chunks)
    assert 4 in result  # chunks[3] → page 4
    assert 16 in result  # chunks[15] → page 16


# ---------------------------------------------------------------------------
# Unit tests: _apply_corrections
# ---------------------------------------------------------------------------


def test_apply_corrections_basic():
    md = "The equation is x^2 + y^2 = z^3 which is wrong."
    corrections = [
        PageCorrection(
            page_number=1,
            original_snippet="z^3",
            corrected_snippet="z^2",
            issue_type="garbled_math",
        )
    ]
    result = _apply_corrections(md, corrections)
    assert "z^2" in result
    assert "z^3" not in result


def test_apply_corrections_empty_list():
    md = "Original text unchanged."
    result = _apply_corrections(md, [])
    assert result == md


def test_apply_corrections_revert_on_shrink():
    md = "A" * 1000
    corrections = [
        PageCorrection(
            page_number=1,
            original_snippet="A" * 900,
            corrected_snippet="B",
            issue_type="other",
        )
    ]
    result = _apply_corrections(md, corrections)
    # Should revert because result would be ~101 chars vs 1000 (>20% shrink)
    assert result == md


def test_apply_corrections_snippet_not_found():
    md = "The real content here."
    corrections = [
        PageCorrection(
            page_number=1,
            original_snippet="nonexistent snippet",
            corrected_snippet="replacement",
            issue_type="other",
        )
    ]
    result = _apply_corrections(md, corrections)
    assert result == md


# ---------------------------------------------------------------------------
# Unit tests: _build_qa_messages
# ---------------------------------------------------------------------------


def test_build_qa_messages_multimodal_format():
    page_chunks = [(1, "chunk one"), (3, "chunk three")]
    page_images = [(1, "base64img1"), (3, "base64img3")]
    messages = _build_qa_messages(page_chunks, page_images)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    # User content should be a list of content blocks
    content = messages[1]["content"]
    assert isinstance(content, list)

    # Should have image_url blocks
    image_blocks = [b for b in content if b.get("type") == "image_url"]
    assert len(image_blocks) == 2
    assert "base64img1" in image_blocks[0]["image_url"]["url"]


def test_build_qa_messages_missing_image():
    page_chunks = [(1, "chunk one"), (2, "chunk two")]
    page_images = [(1, "base64img1")]  # no image for page 2
    messages = _build_qa_messages(page_chunks, page_images)

    content = messages[1]["content"]
    image_blocks = [b for b in content if b.get("type") == "image_url"]
    assert len(image_blocks) == 1  # only page 1 has an image


# ---------------------------------------------------------------------------
# Integration tests: run_extraction_qa
# ---------------------------------------------------------------------------


def _make_paper_text(markdown: str) -> PaperText:
    return PaperText(full_markdown=markdown, token_estimate=len(markdown) // 4)


@patch("coarse.config.resolve_api_key", return_value="fake-key")
@patch("coarse.extraction_qa._get_page_count", return_value=3)
@patch(
    "coarse.extraction_qa.render_pdf_pages",
    return_value=[(1, "img1"), (2, "img2"), (3, "img3")],
)
def test_run_qa_good_quality_returns_original(mock_render, mock_pages, mock_key):
    from coarse.extraction_qa import run_extraction_qa

    md = "Some $$math$$ content\n<!-- PAGE BREAK -->\nPage 2\n<!-- PAGE BREAK -->\nPage 3"
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL
    mock_client.complete.return_value = ExtractionQAResult(overall_quality="good", corrections=[])

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert result.full_markdown == md


@patch("coarse.config.resolve_api_key", return_value="fake-key")
@patch("coarse.extraction_qa._get_page_count", return_value=2)
@patch("coarse.extraction_qa.render_pdf_pages", return_value=[(1, "img1"), (2, "img2")])
def test_run_qa_with_corrections_patches_markdown(mock_render, mock_pages, mock_key):
    from coarse.extraction_qa import run_extraction_qa

    md = "Here is $$x^3$$ wrong\n<!-- PAGE BREAK -->\nPage 2 text"
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL
    mock_client.complete.return_value = ExtractionQAResult(
        overall_quality="acceptable",
        corrections=[
            PageCorrection(
                page_number=1,
                original_snippet="x^3",
                corrected_snippet="x^2",
                issue_type="garbled_math",
            )
        ],
    )

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert "x^2" in result.full_markdown
    assert "x^3" not in result.full_markdown


@patch("coarse.config.resolve_api_key", return_value="fake-key")
@patch("coarse.extraction_qa._get_page_count", return_value=2)
@patch("coarse.extraction_qa.render_pdf_pages", return_value=[(1, "img1"), (2, "img2")])
def test_run_qa_graceful_failure_on_llm_error(mock_render, mock_pages, mock_key):
    from coarse.extraction_qa import run_extraction_qa

    md = "Some $$math$$ content\n<!-- PAGE BREAK -->\nPage 2"
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL
    mock_client.complete.side_effect = RuntimeError("API error")

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert result.full_markdown == md  # returned original


@patch("coarse.config.resolve_api_key", return_value="fake-key")
@patch("coarse.extraction_qa._get_page_count", return_value=5)
def test_run_qa_skips_when_prefilter_false(mock_pages, mock_key):
    from coarse.extraction_qa import run_extraction_qa

    # Clean text, no math/tables — pre-filter should skip
    md = (
        "This is a clean social science paper with no math. " * 50 + "\n<!-- PAGE BREAK -->\n"
    ) * 4
    md += "Final page of clean content. " * 20
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert result.full_markdown == paper.full_markdown
    mock_client.complete.assert_not_called()  # LLM never called


@patch("coarse.config.resolve_api_key", return_value=None)
def test_run_qa_no_api_key_skips(mock_key):
    from coarse.extraction_qa import run_extraction_qa

    md = "Some $$math$$ content"
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert result.full_markdown == md
    mock_client.complete.assert_not_called()


@patch("coarse.config.resolve_api_key", return_value="fake-key")
@patch("coarse.extraction_qa._get_page_count", return_value=1)
@patch("coarse.extraction_qa.render_pdf_pages", return_value=[(1, "img1")])
def test_run_qa_single_page_pdf(mock_render, mock_pages, mock_key):
    from coarse.extraction_qa import run_extraction_qa

    md = "Single page with $$math$$"
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL
    mock_client.complete.return_value = ExtractionQAResult(overall_quality="good", corrections=[])

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert result.full_markdown == md


@patch("coarse.config.resolve_api_key", return_value="fake-key")
@patch("coarse.extraction_qa._get_page_count", return_value=3)
@patch(
    "coarse.extraction_qa.render_pdf_pages",
    return_value=[(1, "img1"), (2, "img2"), (3, "img3")],
)
def test_run_qa_empty_corrections_list(mock_render, mock_pages, mock_key):
    from coarse.extraction_qa import run_extraction_qa

    md = "Math $$y=mx+b$$\n<!-- PAGE BREAK -->\nPage 2\n<!-- PAGE BREAK -->\nPage 3"
    paper = _make_paper_text(md)

    mock_client = MagicMock()
    mock_client._model = VISION_MODEL
    mock_client.complete.return_value = ExtractionQAResult(
        overall_quality="acceptable", corrections=[]
    )

    result = run_extraction_qa(Path("/fake.pdf"), paper, mock_client)
    assert result.full_markdown == md
