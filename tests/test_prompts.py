from coarse.prompts import (
    CROSSREF_SYSTEM,
    CRITIQUE_SYSTEM,
    OVERVIEW_SYSTEM,
    SECTION_SYSTEM,
    STRUCTURE_SYSTEM,
    crossref_user,
    critique_user,
    overview_user,
    section_user,
    structure_user,
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


# --- structure_user ---

def test_structure_user_embeds_text():
    paper = "# My Paper\n\nThis is the abstract.\n\n## Introduction\n\nText here."
    result = structure_user(paper)
    assert paper in result


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
    for prompt in (STRUCTURE_SYSTEM, OVERVIEW_SYSTEM, SECTION_SYSTEM, CROSSREF_SYSTEM, CRITIQUE_SYSTEM):
        assert isinstance(prompt, str)
        assert len(prompt) > 100


def test_section_system_requires_verbatim_quote():
    assert "verbatim" in SECTION_SYSTEM


def test_overview_system_specifies_issue_count():
    assert "4" in OVERVIEW_SYSTEM
    assert "6" in OVERVIEW_SYSTEM


def test_crossref_system_mentions_deduplication():
    assert "duplic" in CROSSREF_SYSTEM.lower()
