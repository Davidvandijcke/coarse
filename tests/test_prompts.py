from coarse.agents.overview import _ASSUMPTION_RELEVANT_TYPES
from coarse.prompts import (
    ASSUMPTION_CHECK_SYSTEM,
    CRITIQUE_SYSTEM,
    CROSSREF_SYSTEM,
    METADATA_SYSTEM,
    OVERVIEW_SYSTEM,
    SECTION_LITERATURE_SYSTEM,
    SECTION_METHODOLOGY_SYSTEM,
    SECTION_PROOF_SYSTEM,
    SECTION_SYSTEM,
    assumption_check_user,
    critique_user,
    crossref_user,
    overview_user,
    section_user,
)
from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    SectionInfo,
    SectionType,
)

# --- Fixtures ---

def make_section(claims=None, definitions=None) -> SectionInfo:
    return SectionInfo(
        number=2,
        title="Identification Strategy",
        text="We exploit a sharp RD design around the threshold c = 0.5.",
        section_type=SectionType.METHODOLOGY,
        claims=claims or [],
        definitions=definitions or [],
    )


def make_overview() -> OverviewFeedback:
    return OverviewFeedback(
        issues=[
            OverviewIssue(title="Estimand Ambiguity", body="The estimand is not clearly defined."),
            OverviewIssue(title="Weak First Stage", body="Instrument relevance is questionable."),
            OverviewIssue(title="Robustness Checks Missing", body="No sensitivity analysis provided."),
            OverviewIssue(title="Generalizability Overstated", body="External validity claims are too broad."),
        ]
    )


def make_comments() -> list[DetailedComment]:
    return [
        DetailedComment(
            number=1,
            title="Undefined bandwidth selector",
            quote="We exploit a sharp RD design around the threshold c = 0.5.",
            feedback="The bandwidth choice is not justified.",
        ),
        DetailedComment(
            number=2,
            title="Missing continuity assumption",
            quote="around the threshold c = 0.5",
            feedback="The continuity assumption for potential outcomes is never stated.",
        ),
    ]


# --- overview_user ---

def test_overview_user_embeds_title_and_abstract():
    title = "Regression Discontinuity and Distribution"
    abstract = "We study treatment effects near a threshold using RD."
    sections_summary = "1. Introduction: claims about RD validity"
    result = overview_user(title, abstract, sections_summary)
    assert title in result
    assert abstract in result


# --- section_user ---

def test_section_user_embeds_section_text():
    sec = make_section()
    result = section_user("My Paper", sec)
    assert sec.text in result
    assert sec.title in result


def test_section_user_empty_claims_handled():
    sec = make_section(claims=[], definitions=[])
    result = section_user("My Paper", sec)
    assert sec.text in result
    # no exception raised


def test_section_user_with_claims_and_defs():
    sec = make_section(
        claims=["RD identifies local ATE", "Bandwidth follows MSE criterion"],
        definitions=["c = 0.5: the cutoff value"],
    )
    result = section_user("Test Paper", sec)
    assert "RD identifies local ATE" in result
    assert "c = 0.5: the cutoff value" in result


# --- crossref_user ---

def test_crossref_user_embeds_all_comments():
    paper = "We exploit a sharp RD design around the threshold c = 0.5."
    overview = make_overview()
    comments = make_comments()
    result = crossref_user(paper, overview, comments)
    assert "Undefined bandwidth selector" in result
    assert "Missing continuity assumption" in result


def test_crossref_user_embeds_paper_text():
    paper = "Unique paper content for verification purposes."
    overview = make_overview()
    comments = make_comments()
    result = crossref_user(paper, overview, comments)
    assert paper in result


# --- critique_user ---

def test_critique_user_embeds_overview_titles():
    overview = make_overview()
    comments = make_comments()
    result = critique_user(overview, comments)
    assert "Estimand Ambiguity" in result
    assert "Weak First Stage" in result


def test_critique_user_embeds_comments():
    overview = make_overview()
    comments = make_comments()
    result = critique_user(overview, comments)
    assert "Undefined bandwidth selector" in result
    assert "Missing continuity assumption" in result


# --- System prompt constants ---

def test_all_system_prompts_are_nonempty_strings():
    for prompt in (
        METADATA_SYSTEM, OVERVIEW_SYSTEM, SECTION_SYSTEM,
        CROSSREF_SYSTEM, CRITIQUE_SYSTEM, ASSUMPTION_CHECK_SYSTEM,
    ):
        assert isinstance(prompt, str)
        assert len(prompt) > 50


def test_section_system_requires_verbatim_quote():
    assert "verbatim" in SECTION_SYSTEM


def test_overview_system_specifies_issue_count():
    assert "4" in OVERVIEW_SYSTEM
    assert "6" in OVERVIEW_SYSTEM


def test_crossref_system_mentions_deduplication():
    assert "duplic" in CROSSREF_SYSTEM.lower()


# --- Assumption checker ---

def test_assumption_check_system_includes_tone_and_confidence():
    assert "constructive colleague" in ASSUMPTION_CHECK_SYSTEM
    assert "rederive" in ASSUMPTION_CHECK_SYSTEM


def test_assumption_check_system_has_four_steps():
    for step in ("STEP 1", "STEP 2", "STEP 3", "STEP 4"):
        assert step in ASSUMPTION_CHECK_SYSTEM


def test_assumption_check_system_lists_common_mismatches():
    for pattern in ("i.i.d.", "panel", "continuity", "discrete", "stationarity"):
        assert pattern.lower() in ASSUMPTION_CHECK_SYSTEM.lower()


def test_assumption_check_user_references_procedure():
    result = assumption_check_user("Test Paper", "some text")
    assert "4-step" in result


def test_section_prompts_include_latex_preservation_instruction():
    latex_phrase = "do not render or interpret LaTeX"
    prompts = (
        SECTION_SYSTEM, SECTION_PROOF_SYSTEM,
        SECTION_METHODOLOGY_SYSTEM, SECTION_LITERATURE_SYSTEM,
    )
    for prompt in prompts:
        assert latex_phrase in prompt


def test_assumption_relevant_types_includes_introduction():
    assert SectionType.INTRODUCTION in _ASSUMPTION_RELEVANT_TYPES


# --- Engagement pattern & confidence calibration ---

def test_section_prompts_include_engagement_pattern():
    """All section system prompts should include the engagement pattern."""
    for prompt in (SECTION_SYSTEM, SECTION_PROOF_SYSTEM, SECTION_METHODOLOGY_SYSTEM):
        assert "thought process" in prompt
        assert "initially expected" in prompt.lower() or "found confusing" in prompt.lower()


def test_section_prompts_include_confidence_calibration():
    """Section prompts should instruct on confidence levels."""
    for prompt in (SECTION_SYSTEM, SECTION_PROOF_SYSTEM, SECTION_METHODOLOGY_SYSTEM):
        assert '"high"' in prompt
        assert '"medium"' in prompt
        assert '"low"' in prompt


def test_section_prompts_include_remediation_specificity():
    """Section prompts should require concrete fix forms."""
    for prompt in (SECTION_SYSTEM, SECTION_PROOF_SYSTEM, SECTION_METHODOLOGY_SYSTEM):
        assert "Rewrite [quoted text]" in prompt or "Rewrite" in prompt


def test_critique_system_includes_confidence_filtering():
    """Critique system should instruct to remove low-confidence comments."""
    assert "low" in CRITIQUE_SYSTEM.lower()
    assert "confidence" in CRITIQUE_SYSTEM.lower()


# --- Cross-section notation context ---

def test_section_user_with_all_sections_includes_notation():
    """section_user should include notation from other sections when all_sections is passed."""
    sec = make_section(definitions=["c = 0.5: the cutoff value"])
    other_sec = SectionInfo(
        number=1, title="Model Setup", text="Define theta.",
        section_type=SectionType.INTRODUCTION,
        definitions=["theta: model parameter", "beta: treatment effect"],
    )
    result = section_user("Test Paper", sec, all_sections=[other_sec, sec])
    assert "theta: model parameter" in result
    assert "Notation & Definitions" in result
    # Should NOT include definitions from the current section in the notation block
    assert result.count("c = 0.5: the cutoff value") == 1  # only in own defs block


def test_section_user_without_all_sections_no_notation():
    """section_user without all_sections should not have notation block."""
    sec = make_section()
    result = section_user("Test Paper", sec)
    assert "Notation & Definitions from Other Sections" not in result
