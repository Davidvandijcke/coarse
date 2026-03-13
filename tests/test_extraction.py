"""Tests for coarse.extraction."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from coarse.extraction import (
    SUPPORTED_EXTENSIONS,
    _estimate_tokens,
    _extract_latex_regex,
    compute_garble_ratio,
    extract_file,
    extract_text,
    normalize_mistral_artifacts,
    normalize_ocr_garble,
)
from coarse.types import ExtractionError, PaperText


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

    mock_converter_cls = MagicMock()
    mock_converter_cls.return_value.convert.return_value = mock_result

    # Mock at sys.modules level to avoid importing real docling (pulls in torch)
    mock_docling = MagicMock()
    mock_docling.document_converter.DocumentConverter = mock_converter_cls

    with patch("coarse.config.resolve_api_key", return_value=None):
        with patch.dict("sys.modules", {
            "docling": mock_docling,
            "docling.document_converter": mock_docling.document_converter,
        }):
            result = extract_text(minimal_pdf, use_cache=False)

    assert "Docling Fallback" in result.full_markdown


def test_all_backends_fail(minimal_pdf: Path) -> None:
    """When all backends fail, raises ValueError."""
    with patch("coarse.config.resolve_api_key", return_value=None):
        with patch.dict(
            "sys.modules",
            {"docling": None, "docling.document_converter": None},
        ):
            with pytest.raises(ValueError, match="no extraction backend"):
                extract_text(minimal_pdf, use_cache=False)


# --- Garble detection and normalization ---


def test_compute_garble_ratio_clean_text():
    """Clean text should have zero garble ratio."""
    assert compute_garble_ratio("This is clean text with LaTeX $x^2$.") == 0.0


def test_compute_garble_ratio_garbled_text():
    """Text with OCR artifacts should have nonzero garble ratio."""
    garbled = "The ®nite case shows /C40x/C41 is naõÈve"
    ratio = compute_garble_ratio(garbled)
    assert ratio > 0.0


def test_compute_garble_ratio_empty():
    assert compute_garble_ratio("") == 0.0


def test_normalize_ocr_garble_fixes_known_patterns():
    """Known garble patterns should be fixed by normalization."""
    garbled = "The ®nite integral over /C40a, b/C41 is naõÈve"
    result = normalize_ocr_garble(garbled)
    assert "finite" in result
    assert "(" in result
    assert ")" in result
    assert "naïve" in result
    assert "®nite" not in result
    assert "/C40" not in result


def test_normalize_ocr_garble_preserves_clean_text():
    """Clean text should not be altered by normalization."""
    clean = "The finite integral over (a, b) is well-defined."
    assert normalize_ocr_garble(clean) == clean


def test_extract_text_sets_garble_ratio(minimal_pdf: Path, mock_ocr_pages) -> None:
    """Extraction should compute and store garble ratio."""
    with patch("litellm.ocr", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_text(minimal_pdf, use_cache=False)
    assert hasattr(result, "garble_ratio")
    assert result.garble_ratio == 0.0  # clean mock data


def test_extract_text_normalizes_garbled_ocr(minimal_pdf: Path) -> None:
    """Garbled OCR output should be auto-normalized."""
    garbled_pages = ["The ®nite case shows /C40x/C41"]
    with patch("litellm.ocr", return_value=_mock_ocr_response(garbled_pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "finite" in result.full_markdown
    assert "®nite" not in result.full_markdown


# --- Mistral artifact normalization ---


def test_normalize_mistral_glyph_mapping():
    """Known glyph[...] patterns should be replaced with Unicode."""
    text = "Let glyph[lscript] be a loss, glyph[epsilon1] > 0, glyph[element] S"
    result = normalize_mistral_artifacts(text)
    assert "ℓ" in result
    assert "ε" in result
    assert "∈" in result
    assert "glyph[" not in result


def test_normalize_mistral_unknown_glyph_preserved():
    """Unknown glyph names should be left as-is."""
    text = "glyph[unknownsymbol] stays"
    result = normalize_mistral_artifacts(text)
    assert "glyph[unknownsymbol]" in result


def test_normalize_mistral_lscript():
    """/lscript should become ℓ."""
    assert normalize_mistral_artifacts("the /lscript norm") == "the ℓ norm"


def test_normalize_mistral_html_entities():
    """HTML entities should be unescaped."""
    text = "x &gt; 0 and y &lt; 1 and &amp; done"
    result = normalize_mistral_artifacts(text)
    assert "x > 0" in result
    assert "y < 1" in result
    assert "& done" in result


def test_normalize_mistral_formula_not_decoded():
    """<!-- formula-not-decoded --> markers should be removed."""
    text = "see equation <!-- formula-not-decoded --> above"
    result = normalize_mistral_artifacts(text)
    assert "formula-not-decoded" not in result
    assert "see equation  above" in result


def test_normalize_mistral_clean_text_preserved():
    """Clean text should not be altered."""
    clean = "The finite integral over (a, b) is well-defined."
    assert normalize_mistral_artifacts(clean) == clean


def test_garble_ratio_detects_mistral_artifacts():
    """Garble ratio should detect glyph[...] and /lscript patterns."""
    text = "Let glyph[lscript] be /lscript norm"
    ratio = compute_garble_ratio(text)
    assert ratio > 0.0


def test_extract_text_normalizes_mistral_artifacts(minimal_pdf: Path) -> None:
    """Mistral OCR artifacts should be normalized during extraction."""
    pages = ["Let glyph[lscript] &gt; 0 with <!-- formula-not-decoded --> here"]
    with patch("litellm.ocr", return_value=_mock_ocr_response(pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_text(minimal_pdf, use_cache=False)
    assert "ℓ" in result.full_markdown
    assert "> 0" in result.full_markdown
    assert "glyph[" not in result.full_markdown
    assert "formula-not-decoded" not in result.full_markdown


# ---------------------------------------------------------------------------
# Multi-format extraction tests (extract_file)
# ---------------------------------------------------------------------------


def test_extract_file_txt(tmp_path: Path) -> None:
    """Plain text files are read as-is with garble_ratio=0.0."""
    txt = tmp_path / "paper.txt"
    txt.write_text("This is a plain text paper.\nWith multiple lines.", encoding="utf-8")
    result = extract_file(txt, use_cache=False)
    assert isinstance(result, PaperText)
    assert "plain text paper" in result.full_markdown
    assert result.garble_ratio == 0.0
    assert result.token_estimate > 0


def test_extract_file_md(tmp_path: Path) -> None:
    """Markdown files preserve headings."""
    md = tmp_path / "paper.md"
    md.write_text("# Introduction\n\nSome content.\n\n## Methods\n\nMore content.", encoding="utf-8")
    result = extract_file(md, use_cache=False)
    assert "# Introduction" in result.full_markdown
    assert "## Methods" in result.full_markdown
    assert result.garble_ratio == 0.0


def test_extract_file_tex(tmp_path: Path) -> None:
    """LaTeX files have headings converted to markdown."""
    tex = tmp_path / "paper.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        "\\usepackage{amsmath}\n"
        "\\begin{document}\n"
        "\\section{Introduction}\n"
        "This paper studies $x^2$.\n"
        "\\subsection{Background}\n"
        "Some background.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = extract_file(tex, use_cache=False)
    assert "# Introduction" in result.full_markdown
    assert "## Background" in result.full_markdown
    assert "$x^2$" in result.full_markdown
    assert "\\documentclass" not in result.full_markdown
    assert result.garble_ratio == 0.0


def test_extract_file_unsupported(tmp_path: Path) -> None:
    """Unsupported extensions raise ExtractionError."""
    bad = tmp_path / "paper.xyz"
    bad.write_text("content", encoding="utf-8")
    with pytest.raises(ExtractionError, match="Unsupported file format"):
        extract_file(bad, use_cache=False)


def test_extract_file_missing() -> None:
    """Missing files raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        extract_file("/nonexistent/paper.txt")


def test_extract_file_pdf_delegates(minimal_pdf: Path, mock_ocr_pages) -> None:
    """PDF files delegate to extract_text."""
    with patch("litellm.ocr", return_value=_mock_ocr_response(mock_ocr_pages)):
        with patch("coarse.config.resolve_api_key", return_value="test-key"):
            result = extract_file(minimal_pdf, use_cache=False)
    assert isinstance(result, PaperText)
    assert "# Test Paper" in result.full_markdown


def test_extract_file_caching(tmp_path: Path) -> None:
    """Non-PDF files are cached after first extraction."""
    txt = tmp_path / "paper.txt"
    txt.write_text("Cached content.", encoding="utf-8")
    r1 = extract_file(txt, use_cache=True)
    # Modify file content — but cache should still be used (same mtime check)
    r2 = extract_file(txt, use_cache=True)
    assert r1.full_markdown == r2.full_markdown


def test_extract_latex_heading_conversion() -> None:
    """All LaTeX heading levels are correctly converted."""
    result = _extract_latex_regex.__wrapped__(Path("/dev/null")) if hasattr(
        _extract_latex_regex, "__wrapped__"
    ) else None
    # Test the regex directly
    from coarse.extraction import _LATEX_HEADING_RE, _LATEX_HEADING_LEVEL
    import re

    test_cases = [
        ("\\section{Intro}", "# Intro"),
        ("\\subsection{Methods}", "## Methods"),
        ("\\subsubsection{Details}", "### Details"),
        ("\\paragraph{Note}", "#### Note"),
        ("\\section*{Starred}", "# Starred"),
    ]
    for latex, expected_md in test_cases:
        converted = _LATEX_HEADING_RE.sub(
            lambda m: f"{_LATEX_HEADING_LEVEL[m.group(1)]} {m.group(2)}", latex
        )
        assert converted == expected_md, f"{latex} → {converted}, expected {expected_md}"


def test_extract_latex_preserves_math(tmp_path: Path) -> None:
    """Math content survives LaTeX extraction (may be converted to $$ format by Docling)."""
    tex = tmp_path / "math.tex"
    tex.write_text(
        "\\begin{document}\n"
        "\\section{Theory}\n"
        "Consider $x^2 + y^2 = z^2$ and\n"
        "\\begin{equation}\n"
        "  E = mc^2\n"
        "\\end{equation}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = extract_file(tex, use_cache=False)
    # Inline math preserved
    assert "x^2" in result.full_markdown
    # Display math preserved (either as \begin{equation} or $$ depending on backend)
    assert "E = mc^2" in result.full_markdown


def test_extract_latex_strips_preamble(tmp_path: Path) -> None:
    """LaTeX preamble noise is stripped."""
    tex = tmp_path / "preamble.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\title{My Paper}\n"
        "\\author{Author}\n"
        "\\date{2026}\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        "\\section{Intro}\n"
        "Content here.\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    result = extract_file(tex, use_cache=False)
    assert "\\documentclass" not in result.full_markdown
    assert "\\usepackage" not in result.full_markdown
    assert "\\title" not in result.full_markdown
    assert "\\maketitle" not in result.full_markdown
    assert "# Intro" in result.full_markdown
    assert "Content here." in result.full_markdown


def test_supported_extensions_includes_all_formats() -> None:
    """SUPPORTED_EXTENSIONS includes all documented formats."""
    for ext in [".pdf", ".txt", ".md", ".tex", ".latex", ".html", ".htm", ".docx", ".epub"]:
        assert ext in SUPPORTED_EXTENSIONS
