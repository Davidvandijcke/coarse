"""Tests for coarse.structure — markdown heading parsing + metadata LLM call."""
from unittest.mock import MagicMock

import pytest

from coarse.structure import (
    _classify_section_type,
    _extract_abstract,
    _extract_title,
    _parse_sections_from_markdown,
    analyze_structure,
)
from coarse.types import (
    PaperMetadata,
    PaperStructure,
    PaperText,
    SectionInfo,
    SectionType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_MARKDOWN = """\
# My Paper Title

## Abstract

This is the abstract of the paper.

## 1 Introduction

Introduction text here. We study important things.

## 2 Methods

We use OLS regression to estimate the effect.

### 2.1 Data

The data comes from a survey of 1000 households.

## 3 Results

The main result is statistically significant.

## 4 Discussion

We discuss implications of our findings.

## 5 Conclusion

In conclusion, we find evidence of the effect.

## References

[1] Smith et al. (2020). Some paper.
"""


def make_paper_text(markdown: str = SAMPLE_MARKDOWN) -> PaperText:
    return PaperText(full_markdown=markdown, token_estimate=len(markdown) // 4)


# ---------------------------------------------------------------------------
# _parse_sections_from_markdown tests
# ---------------------------------------------------------------------------

def test_parse_sections_correct_count():
    """Correct number of sections extracted from headings."""
    sections = _parse_sections_from_markdown(SAMPLE_MARKDOWN)
    # # My Paper Title, ## Abstract, ## 1 Introduction, ## 2 Methods,
    # ### 2.1 Data, ## 3 Results, ## 4 Discussion, ## 5 Conclusion, ## References
    assert len(sections) == 9


def test_parse_sections_titles():
    """Section titles extracted correctly."""
    sections = _parse_sections_from_markdown(SAMPLE_MARKDOWN)
    titles = [s.title for s in sections]
    assert "My Paper Title" in titles
    assert "Abstract" in titles
    assert "1 Introduction" in titles
    assert "2 Methods" in titles
    assert "References" in titles


def test_parse_sections_text_is_substring():
    """Each section's text is a substring of the full markdown."""
    sections = _parse_sections_from_markdown(SAMPLE_MARKDOWN)
    for section in sections:
        if section.text:
            assert section.text in SAMPLE_MARKDOWN


def test_parse_sections_text_between_headings():
    """Section text contains content between its heading and the next."""
    sections = _parse_sections_from_markdown(SAMPLE_MARKDOWN)
    abstract = next(s for s in sections if s.title == "Abstract")
    assert "This is the abstract of the paper." in abstract.text

    methods = next(s for s in sections if s.title == "2 Methods")
    assert "OLS regression" in methods.text


def test_parse_sections_empty_markdown():
    """Empty markdown produces single section."""
    sections = _parse_sections_from_markdown("")
    assert len(sections) == 1
    assert sections[0].title == "Full Document"


def test_parse_sections_no_headings():
    """Markdown with no headings produces a single section."""
    sections = _parse_sections_from_markdown("Just plain text without any headings.")
    assert len(sections) == 1
    assert sections[0].section_type == SectionType.OTHER


def test_parse_sections_preserves_numbering():
    """Sections are numbered sequentially."""
    sections = _parse_sections_from_markdown(SAMPLE_MARKDOWN)
    for i, section in enumerate(sections):
        assert section.number == i + 1


# ---------------------------------------------------------------------------
# _classify_section_type tests
# ---------------------------------------------------------------------------

def test_classify_introduction():
    assert _classify_section_type("1 Introduction") == SectionType.INTRODUCTION


def test_classify_methodology():
    assert _classify_section_type("3 Methodology") == SectionType.METHODOLOGY


def test_classify_results():
    assert _classify_section_type("4 Results and Discussion") == SectionType.RESULTS


def test_classify_references():
    assert _classify_section_type("References") == SectionType.REFERENCES


def test_classify_related_work():
    assert _classify_section_type("2 Related Work") == SectionType.RELATED_WORK


def test_classify_appendix():
    assert _classify_section_type("Appendix A") == SectionType.APPENDIX


def test_classify_unknown():
    assert _classify_section_type("7 Widgets and Gadgets") == SectionType.OTHER


# ---------------------------------------------------------------------------
# _extract_title tests
# ---------------------------------------------------------------------------

def test_extract_title_from_heading():
    assert _extract_title(SAMPLE_MARKDOWN) == "My Paper Title"


def test_extract_title_fallback():
    assert _extract_title("Just a line\nAnother line") == "Just a line"


def test_extract_title_empty():
    assert _extract_title("") == "Untitled"


# ---------------------------------------------------------------------------
# _extract_abstract tests
# ---------------------------------------------------------------------------

def test_extract_abstract_from_section():
    sections = _parse_sections_from_markdown(SAMPLE_MARKDOWN)
    abstract = _extract_abstract(sections, SAMPLE_MARKDOWN)
    assert "abstract of the paper" in abstract


def test_extract_abstract_fallback_no_abstract_section():
    md = "# Title\n\nSome preamble text.\n\n## Introduction\n\nBody."
    sections = _parse_sections_from_markdown(md)
    # No ABSTRACT section, should fall back to preamble
    abstract = _extract_abstract(sections, md)
    # First section is "Title" which is not ABSTRACT, so fallback should trigger
    assert len(abstract) > 0


# ---------------------------------------------------------------------------
# analyze_structure (integration with mock LLM)
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_client():
    client = MagicMock()
    client.complete.return_value = PaperMetadata(
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
    )
    return client


def test_analyze_structure_returns_paper_structure(mock_client):
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    assert isinstance(result, PaperStructure)
    assert result.title == "My Paper Title"
    assert result.domain == "social_sciences/economics"
    assert len(result.sections) > 0


def test_analyze_structure_sections_have_text(mock_client):
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    # At least some sections should have non-empty text
    has_text = any(len(s.text) > 0 for s in result.sections)
    assert has_text


def test_analyze_structure_calls_llm_for_metadata(mock_client):
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)
    mock_client.complete.assert_called_once()
    call_args = mock_client.complete.call_args
    assert call_args[0][1] is PaperMetadata


def test_analyze_structure_uses_low_temperature(mock_client):
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)
    call_kwargs = mock_client.complete.call_args[1]
    assert call_kwargs["temperature"] <= 0.2


def test_analyze_structure_low_max_tokens(mock_client):
    """Metadata call should use low max_tokens (not 16K+)."""
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)
    call_kwargs = mock_client.complete.call_args[1]
    assert call_kwargs["max_tokens"] <= 512


def test_analyze_structure_propagates_llm_error(mock_client):
    """LLM error during metadata falls back to defaults."""
    mock_client.complete.side_effect = RuntimeError("LLM unavailable")
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    # Should still return a structure with default metadata
    assert result.domain == "unknown"
    assert result.taxonomy == "academic/research_paper"
