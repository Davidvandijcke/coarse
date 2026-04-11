import json
import math

import pytest
from pydantic import ValidationError

from coarse.types import (
    CostEstimate,
    CostStage,
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    PaperText,
    Review,
    SectionInfo,
    SectionType,
)


def make_section(number: int, section_type: SectionType = SectionType.OTHER) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=f"Section {number}",
        text="Some text.",
        section_type=section_type,
    )


def make_issue(n: int) -> OverviewIssue:
    return OverviewIssue(title=f"Issue {n}", body=f"Body {n}")


def make_comment(n: int) -> DetailedComment:
    return DetailedComment(
        number=n,
        title=f"Comment {n}",
        quote="Verbatim quote from paper.",
        feedback="This needs fixing.",
    )


def make_review(n_comments: int = 2) -> Review:
    return Review(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="03/03/2026",
        overall_feedback=OverviewFeedback(issues=[make_issue(i) for i in range(1, 5)]),
        detailed_comments=[make_comment(i) for i in range(1, n_comments + 1)],
    )


# --- PaperText ---


def test_paper_text_basic():
    pt = PaperText(full_markdown="# Full\nPage one text.\nPage two text.", token_estimate=150)
    assert pt.full_markdown.startswith("# Full")
    assert pt.token_estimate == 150


def test_paper_text_empty():
    pt = PaperText(full_markdown="All text as one block.", token_estimate=50)
    assert pt.full_markdown == "All text as one block."


# --- PaperStructure ---


def test_paper_structure_sections_list():
    all_types = list(SectionType)
    sections = [make_section(i, st) for i, st in enumerate(all_types, start=1)]
    ps = PaperStructure(
        title="My Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="Abstract text.",
        sections=sections,
    )
    assert len(ps.sections) == len(all_types)
    for sec, st in zip(ps.sections, all_types):
        assert sec.section_type == st


def test_paper_structure_defaults_to_manuscript_form():
    """document_form must default to 'manuscript' so existing callers that
    don't pass it get the strict peer-review path."""
    ps = PaperStructure(
        title="t",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="a",
        sections=[make_section(1, SectionType.INTRODUCTION)],
    )
    assert ps.document_form == "manuscript"


@pytest.mark.parametrize(
    "form",
    ["manuscript", "outline", "draft", "proposal", "report", "notes", "other"],
)
def test_paper_structure_accepts_all_document_forms(form):
    """Every value in the DocumentForm literal must round-trip through the
    Pydantic model without raising."""
    ps = PaperStructure(
        title="t",
        domain="x",
        taxonomy="y",
        abstract="a",
        sections=[make_section(1, SectionType.INTRODUCTION)],
        document_form=form,
    )
    assert ps.document_form == form


def test_paper_structure_rejects_unknown_document_form():
    """Arbitrary strings must fail validation — the Literal type is the
    single source of truth for what the pipeline can branch on."""
    with pytest.raises(ValidationError):
        PaperStructure(
            title="t",
            domain="x",
            taxonomy="y",
            abstract="a",
            sections=[make_section(1, SectionType.INTRODUCTION)],
            document_form="thesis",  # not in DocumentForm
        )


# --- SectionType ---


def test_section_type_enum_values():
    expected = {
        "ABSTRACT": "abstract",
        "INTRODUCTION": "introduction",
        "RELATED_WORK": "related_work",
        "METHODOLOGY": "methodology",
        "RESULTS": "results",
        "DISCUSSION": "discussion",
        "CONCLUSION": "conclusion",
        "APPENDIX": "appendix",
        "REFERENCES": "references",
        "OTHER": "other",
    }
    for name, value in expected.items():
        assert SectionType[name].value == value


# --- OverviewFeedback ---


def test_overview_feedback_count_constraint():
    # Empty is too few (min_length=1)
    with pytest.raises(ValidationError):
        OverviewFeedback(issues=[])

    # Any positive count is valid (no upper cap)
    for count in (1, 4, 5, 6, 10):
        fb = OverviewFeedback(issues=[make_issue(i) for i in range(count)])
        assert len(fb.issues) == count


# --- DetailedComment ---

_LONG_QUOTE = "This is a verbatim quote from the paper text."


def test_detailed_comment_status_default():
    c = DetailedComment(
        number=1,
        title="Issue",
        quote=_LONG_QUOTE,
        feedback="Feedback text.",
    )
    assert c.status == "Pending"


def test_detailed_comment_confidence_default():
    c = DetailedComment(
        number=1,
        title="Issue",
        quote=_LONG_QUOTE,
        feedback="Feedback text.",
    )
    assert c.confidence == "medium"


def test_detailed_comment_confidence_values():
    for conf in ("high", "medium", "low"):
        c = DetailedComment(
            number=1,
            title="Issue",
            quote=_LONG_QUOTE,
            feedback="Feedback text.",
            confidence=conf,
        )
        assert c.confidence == conf


def test_detailed_comment_confidence_invalid():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DetailedComment(
            number=1,
            title="Issue",
            quote=_LONG_QUOTE,
            feedback="Feedback text.",
            confidence="very_high",
        )


def test_paper_text_garble_ratio_default():
    pt = PaperText(full_markdown="text", token_estimate=1)
    assert pt.garble_ratio == 0.0


def test_paper_text_garble_ratio_set():
    pt = PaperText(full_markdown="text", token_estimate=1, garble_ratio=0.05)
    assert pt.garble_ratio == 0.05


def test_detailed_comment_status_invalid():
    with pytest.raises(ValidationError):
        DetailedComment(
            number=1,
            title="Issue",
            quote=_LONG_QUOTE,
            feedback="Feedback text.",
            status="Approved",  # type: ignore[arg-type]
        )


# --- Review ---


def test_review_roundtrip_json():
    review = make_review(n_comments=3)
    serialized = review.model_dump_json()
    deserialized = Review.model_validate(json.loads(serialized))
    assert deserialized == review


# --- CostEstimate ---


def test_cost_estimate_total_matches_sum():
    stages = [
        CostStage(
            name="structure",
            model="gpt-4o",
            estimated_tokens_in=1000,
            estimated_tokens_out=500,
            estimated_cost_usd=0.01,
        ),
        CostStage(
            name="overview",
            model="gpt-4o",
            estimated_tokens_in=2000,
            estimated_tokens_out=800,
            estimated_cost_usd=0.02,
        ),
        CostStage(
            name="section",
            model="gpt-4o",
            estimated_tokens_in=3000,
            estimated_tokens_out=1200,
            estimated_cost_usd=0.03,
        ),
    ]
    total = sum(s.estimated_cost_usd for s in stages)
    est = CostEstimate(stages=stages, total_cost_usd=total)
    assert math.isclose(est.total_cost_usd, 0.06, rel_tol=1e-9)


# --- Quote min_length ---


def test_detailed_comment_rejects_short_quote():
    """Quotes shorter than 20 characters should be rejected by Pydantic validation."""
    with pytest.raises(ValidationError):
        DetailedComment(
            number=1,
            title="Issue",
            quote="Too short.",
            feedback="Feedback text.",
        )


def test_detailed_comment_accepts_long_quote():
    """Quotes with 20+ characters should be accepted."""
    c = DetailedComment(
        number=1,
        title="Issue",
        quote="This is a sufficiently long quote from the paper.",
        feedback="Feedback text.",
    )
    assert len(c.quote) >= 20


# --- OverviewFeedback new fields: recommendation & revision_targets ---


def test_overview_feedback_recommendation_default():
    """recommendation defaults to empty string."""
    fb = OverviewFeedback(issues=[make_issue(1)])
    assert fb.recommendation == ""


def test_overview_feedback_revision_targets_default():
    """revision_targets defaults to empty list."""
    fb = OverviewFeedback(issues=[make_issue(1)])
    assert fb.revision_targets == []


def test_overview_feedback_with_recommendation():
    """OverviewFeedback accepts a non-empty recommendation."""
    fb = OverviewFeedback(
        issues=[make_issue(1)],
        recommendation="Major revision. The identification needs work.",
    )
    assert fb.recommendation == "Major revision. The identification needs work."


def test_overview_feedback_with_revision_targets():
    """OverviewFeedback accepts non-empty revision_targets."""
    targets = [
        "Add formal sensitivity analysis.",
        "Include simulation study.",
    ]
    fb = OverviewFeedback(
        issues=[make_issue(1)],
        revision_targets=targets,
    )
    assert fb.revision_targets == targets
    assert len(fb.revision_targets) == 2


def test_review_roundtrip_json_with_new_fields():
    """Review with recommendation + revision_targets survives JSON roundtrip."""
    overview = OverviewFeedback(
        issues=[make_issue(i) for i in range(1, 5)],
        recommendation="Minor revision. Address the robustness concerns.",
        revision_targets=[
            "Add bootstrap confidence intervals.",
            "Discuss external validity limitations.",
        ],
    )
    review = Review(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="03/03/2026",
        overall_feedback=overview,
        detailed_comments=[make_comment(1)],
    )
    serialized = review.model_dump_json()
    deserialized = Review.model_validate(json.loads(serialized))
    assert deserialized == review
    assert deserialized.overall_feedback.recommendation == overview.recommendation
    assert deserialized.overall_feedback.revision_targets == overview.revision_targets
