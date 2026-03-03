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
    PageContent,
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
    pages = [
        PageContent(page_num=1, text="Page one text."),
        PageContent(page_num=2, text="Page two text."),
    ]
    pt = PaperText(full_markdown="# Full\nPage one text.\nPage two text.", pages=pages, token_estimate=150)
    assert pt.full_markdown.startswith("# Full")
    assert pt.token_estimate == 150
    assert len(pt.pages) == 2


def test_page_content_image_optional():
    p = PageContent(page_num=1, text="Hello")
    assert p.image_b64 is None

    p2 = PageContent(page_num=2, text="World", image_b64="base64data==")
    assert p2.image_b64 == "base64data=="


def test_paper_text_empty_pages():
    pt = PaperText(full_markdown="All text as one block.", pages=[], token_estimate=50)
    assert pt.pages == []
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
    # Too few
    with pytest.raises(ValidationError):
        OverviewFeedback(issues=[make_issue(i) for i in range(3)])

    # Too many
    with pytest.raises(ValidationError):
        OverviewFeedback(issues=[make_issue(i) for i in range(7)])

    # Valid range: 4 to 6
    for count in range(4, 7):
        fb = OverviewFeedback(issues=[make_issue(i) for i in range(count)])
        assert len(fb.issues) == count


# --- DetailedComment ---

def test_detailed_comment_status_default():
    c = DetailedComment(number=1, title="Issue", quote="Quote text.", feedback="Feedback text.")
    assert c.status == "Pending"


def test_detailed_comment_status_invalid():
    with pytest.raises(ValidationError):
        DetailedComment(
            number=1,
            title="Issue",
            quote="Quote text.",
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
        CostStage(name="structure", model="gpt-4o", estimated_tokens_in=1000, estimated_tokens_out=500, estimated_cost_usd=0.01),
        CostStage(name="overview", model="gpt-4o", estimated_tokens_in=2000, estimated_tokens_out=800, estimated_cost_usd=0.02),
        CostStage(name="section", model="gpt-4o", estimated_tokens_in=3000, estimated_tokens_out=1200, estimated_cost_usd=0.03),
    ]
    total = sum(s.estimated_cost_usd for s in stages)
    est = CostEstimate(stages=stages, total_cost_usd=total)
    assert math.isclose(est.total_cost_usd, 0.06, rel_tol=1e-9)
