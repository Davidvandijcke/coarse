"""Tests for coarse.structure — markdown heading parsing + metadata LLM call."""
from unittest.mock import MagicMock

import pytest

from coarse.structure import (
    _classify_section_type,
    _detect_math_sections,
    _detect_math_sections_keyword,
    _extract_abstract,
    _extract_claims_and_definitions,
    _extract_title,
    _is_section_heading,
    _parse_sections_from_markdown,
    analyze_structure,
)
from coarse.types import (
    MathSectionDetection,
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


def _make_mock_client():
    """Create a mock client that handles both metadata and math detection calls."""
    client = MagicMock()

    def _side_effect(messages, response_model, **kwargs):
        if response_model is PaperMetadata:
            return PaperMetadata(
                title="Test Paper Title",
                domain="social_sciences/economics",
                taxonomy="academic/research_paper",
            )
        if response_model is MathSectionDetection:
            return MathSectionDetection(math_section_indices=[])
        raise ValueError(f"Unexpected response_model: {response_model}")

    client.complete.side_effect = _side_effect
    return client


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


def test_extract_title_skips_abstract_heading():
    """When first heading is 'Abstract', title comes from preamble text."""
    md = "My Actual Paper Title\n\n## Abstract\n\nThis is the abstract.\n"
    assert _extract_title(md) == "My Actual Paper Title"


def test_extract_title_skips_section_headings():
    """When all headings are section names, use preamble."""
    md = "A Novel Method for X\n\n## Introduction\n\nIntro text.\n\n## Methods\n\nMethod text.\n"
    assert _extract_title(md) == "A Novel Method for X"


def test_extract_title_prefers_non_section_heading():
    """A heading that isn't a section name is preferred over preamble."""
    md = "# Regression Discontinuity Design\n\n## Abstract\n\nText.\n"
    assert _extract_title(md) == "Regression Discontinuity Design"


def test_is_section_heading():
    assert _is_section_heading("Abstract")
    assert _is_section_heading("1. Introduction")
    assert _is_section_heading("2 Methods")
    assert _is_section_heading("References")
    assert not _is_section_heading("My Paper Title")
    assert not _is_section_heading("Regression Discontinuity Design")


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
    return _make_mock_client()


def test_analyze_structure_returns_paper_structure(mock_client):
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    assert isinstance(result, PaperStructure)
    assert result.title == "Test Paper Title"
    assert result.domain == "social_sciences/economics"
    assert len(result.sections) > 0


def test_analyze_structure_sections_have_text(mock_client):
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    # At least some sections should have non-empty text
    has_text = any(len(s.text) > 0 for s in result.sections)
    assert has_text


def test_analyze_structure_calls_llm_twice(mock_client):
    """LLM is called for both metadata and math section detection."""
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)
    assert mock_client.complete.call_count == 2
    # First call: metadata, second call: math detection
    call_args_list = mock_client.complete.call_args_list
    assert call_args_list[0][0][1] is PaperMetadata
    assert call_args_list[1][0][1] is MathSectionDetection


def test_analyze_structure_uses_low_temperature(mock_client):
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)
    # Both calls should use low temperature
    for c in mock_client.complete.call_args_list:
        assert c[1]["temperature"] <= 0.2


def test_analyze_structure_low_max_tokens(mock_client):
    """Both metadata and math detection calls should use a bounded max_tokens
    budget — not the 4096 default — since the structured output is small.

    Metadata stays tight at 256; math detection needs 1024 so Claude-family
    models have headroom for their prose preamble before emitting the tool
    call (see test_detect_math_sections_passes_large_max_tokens_budget).
    """
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)
    for c in mock_client.complete.call_args_list:
        assert c[1]["max_tokens"] <= 1024


def test_analyze_structure_propagates_llm_error(mock_client):
    """LLM error during metadata falls back to defaults."""
    mock_client.complete.side_effect = RuntimeError("LLM unavailable")
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    # Should still return a structure with default metadata
    assert result.domain == "unknown"
    assert result.taxonomy == "academic/research_paper"


def test_analyze_structure_math_detection_sets_flags():
    """Math detection LLM call sets math_content=True on indicated sections."""
    client = MagicMock()

    def _side_effect(messages, response_model, **kwargs):
        if response_model is PaperMetadata:
            return PaperMetadata(
                title="Test Paper Title",
                domain="statistics/methodology",
                taxonomy="academic/research_paper",
            )
        if response_model is MathSectionDetection:
            # Mark sections at indices 3 and 4 (Methods and Data)
            return MathSectionDetection(math_section_indices=[3, 4])
        raise ValueError(f"Unexpected response_model: {response_model}")

    client.complete.side_effect = _side_effect
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, client)

    math_sections = [s for s in result.sections if s.math_content]
    non_math = [s for s in result.sections if not s.math_content]
    assert len(math_sections) == 2
    assert len(non_math) == len(result.sections) - 2


# ---------------------------------------------------------------------------
# _detect_math_sections tests
# ---------------------------------------------------------------------------

def test_detect_math_sections_sets_flags():
    """LLM-based detection sets math_content on indicated indices."""
    sections = [
        SectionInfo(
            number=1, title="Intro", text="intro text",
            section_type=SectionType.INTRODUCTION,
        ),
        SectionInfo(
            number=2, title="Theory", text="theorem proof lemma",
            section_type=SectionType.OTHER,
        ),
        SectionInfo(
            number=3, title="Results", text="empirical results",
            section_type=SectionType.RESULTS,
        ),
    ]
    client = MagicMock()
    client.complete.return_value = MathSectionDetection(math_section_indices=[1])

    result = _detect_math_sections(sections, client)
    assert not result[0].math_content
    assert result[1].math_content
    assert not result[2].math_content


def test_detect_math_sections_ignores_out_of_range():
    """Out-of-range indices from LLM are silently ignored."""
    sections = [
        SectionInfo(
            number=1, title="Intro", text="text",
            section_type=SectionType.INTRODUCTION,
        ),
    ]
    client = MagicMock()
    client.complete.return_value = MathSectionDetection(math_section_indices=[0, 99])

    result = _detect_math_sections(sections, client)
    assert result[0].math_content  # index 0 is valid
    assert len(result) == 1  # index 99 silently ignored


def test_detect_math_sections_falls_back_on_error():
    """On LLM failure, falls back to keyword detection."""
    sections = [
        SectionInfo(
            number=1, title="Intro", text="intro text",
            section_type=SectionType.INTRODUCTION,
        ),
        SectionInfo(
            number=2, title="Proofs",
            text="We prove the following theorem.",
            section_type=SectionType.APPENDIX,
        ),
    ]
    client = MagicMock()
    client.complete.side_effect = RuntimeError("LLM down")

    result = _detect_math_sections(sections, client)
    assert not result[0].math_content
    assert result[1].math_content  # keyword fallback detects "theorem" and "prove"


def test_detect_math_sections_passes_large_max_tokens_budget():
    """Claude 4-family models write a prose preamble before emitting the
    structured output, so the math detection budget has to be large enough
    to survive that. 256 was too tight in production (Opus 4.6 hit
    finish_reason='length' before any JSON was produced and instructor
    raised InstructorRetryException). We now pass >=1024, and the keyword
    fallback still takes over if the model does exhaust whatever budget
    we pass."""
    sections = [
        SectionInfo(
            number=1, title="Intro", text="intro",
            section_type=SectionType.INTRODUCTION,
        ),
    ]
    client = MagicMock()
    client.complete.return_value = MathSectionDetection(math_section_indices=[])

    _detect_math_sections(sections, client)

    assert client.complete.called
    max_tokens = client.complete.call_args.kwargs.get("max_tokens")
    if max_tokens is None and len(client.complete.call_args.args) >= 3:
        max_tokens = client.complete.call_args.args[2]
    assert max_tokens is not None, "max_tokens must be passed explicitly"
    assert max_tokens >= 1024, (
        f"max_tokens={max_tokens} is too tight for Claude-family preambles; "
        f"256 caused InstructorRetryException in production (see review "
        f"1e786d50)"
    )


def test_detect_math_sections_falls_back_on_instructor_length_limit():
    """The specific production failure mode: instructor raises because the
    model hit finish_reason='length' before emitting any structured output.
    The fallback must still produce a valid result (via keyword detection),
    not crash the pipeline."""
    sections = [
        SectionInfo(
            number=1, title="Intro", text="intro text",
            section_type=SectionType.INTRODUCTION,
        ),
        SectionInfo(
            number=2, title="Empirical Strategy",
            text="We prove that the difference-in-differences estimator "
                 "is consistent under the parallel trends assumption.",
            section_type=SectionType.METHODOLOGY,
        ),
    ]
    client = MagicMock()
    # Mimic instructor's own exception message so the fallback path is
    # exercised with a realistic error.
    client.complete.side_effect = RuntimeError(
        "The output is incomplete due to a max_tokens length limit."
    )

    result = _detect_math_sections(sections, client)
    assert not result[0].math_content
    assert result[1].math_content  # keyword hit on "prove" and "theorem"-adjacent text


# ---------------------------------------------------------------------------
# _detect_math_sections_keyword tests
# ---------------------------------------------------------------------------

def test_keyword_fallback_detects_theorem():
    sections = [
        SectionInfo(
            number=1, title="Theory",
            text="We state the main theorem.",
            section_type=SectionType.OTHER,
        ),
    ]
    result = _detect_math_sections_keyword(sections)
    assert result[0].math_content


def test_keyword_fallback_detects_proof():
    sections = [
        SectionInfo(
            number=1, title="Appendix",
            text="Proof of Lemma 1.",
            section_type=SectionType.APPENDIX,
        ),
    ]
    result = _detect_math_sections_keyword(sections)
    assert result[0].math_content


def test_keyword_fallback_no_match():
    sections = [
        SectionInfo(
            number=1, title="Intro",
            text="This paper studies wages.",
            section_type=SectionType.INTRODUCTION,
        ),
    ]
    result = _detect_math_sections_keyword(sections)
    assert not result[0].math_content


# ---------------------------------------------------------------------------
# _extract_claims_and_definitions tests
# ---------------------------------------------------------------------------

def test_extract_claims_theorem():
    """Extracts theorems as claims."""
    text = """
**Theorem 1.** If X is compact and f is continuous, then f attains its maximum.

Some other text here.
"""
    claims, defs = _extract_claims_and_definitions(text)
    assert len(claims) == 1
    assert "Theorem 1" in claims[0]
    assert "compact" in claims[0]
    assert len(defs) == 0


def test_extract_claims_definition():
    """Extracts definitions into the definitions list."""
    text = """
**Definition 2.** A set S is called open if for every point x in S there exists epsilon > 0.

More text.
"""
    claims, defs = _extract_claims_and_definitions(text)
    assert len(defs) == 1
    assert "Definition 2" in defs[0]
    assert len(claims) == 0


def test_extract_claims_assumption():
    """Extracts assumptions as claims."""
    text = """
Assumption A1. The error terms are independently and identically distributed.

Further discussion follows.
"""
    claims, defs = _extract_claims_and_definitions(text)
    assert len(claims) == 1
    assert "Assumption" in claims[0]
    assert "A1" in claims[0]


def test_extract_claims_multiple():
    """Extracts multiple formal statements from one section."""
    text = """
**Theorem 1.** Result about convergence rates.

**Lemma 2.** A supporting technical result.

**Definition 3.** We define the operator T as follows.

**Assumption 1.** The data generating process satisfies regularity conditions.
"""
    claims, defs = _extract_claims_and_definitions(text)
    assert len(claims) == 3  # theorem, lemma, assumption
    assert len(defs) == 1    # definition


def test_extract_claims_empty_text():
    """No formal statements yields empty lists."""
    claims, defs = _extract_claims_and_definitions("Just plain text with no theorems.")
    assert claims == []
    assert defs == []


def test_extract_claims_truncates_long_statements():
    """Statements over 500 chars are truncated with ellipsis."""
    long_statement = "x " * 300  # 600 chars
    text = f"\nTheorem 1. {long_statement}\n\n"
    claims, defs = _extract_claims_and_definitions(text)
    assert len(claims) == 1
    assert claims[0].endswith("...")
    # The claim entry is "Theorem 1: <truncated>...", so the statement portion is 500 chars
    assert len(claims[0]) <= 520  # "Theorem 1: " prefix + 500 chars + "..."


def test_parse_sections_populates_claims_and_definitions():
    """_parse_sections_from_markdown should populate claims/definitions fields."""
    md = """\
# Paper Title

## Theory

**Theorem 1.** The estimator is consistent under regularity conditions.

**Definition 1.** A function f is Lipschitz if there exists L > 0 such that condition holds.

## Results

The main finding is significant.
"""
    mock_client = _make_mock_client()
    paper_text = PaperText(full_markdown=md, token_estimate=100)
    result = analyze_structure(paper_text, mock_client)
    theory = next(s for s in result.sections if s.title == "Theory")
    assert len(theory.claims) >= 1
    assert len(theory.definitions) >= 1
