"""Tests for coarse.review_stages."""

from __future__ import annotations

from unittest.mock import Mock, patch

from coarse.review_stages import (
    _detect_section_focus,
    _review_section,
    run_editorial_pass,
)
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, SectionInfo, SectionType


def _comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote="This is a sufficiently long quote from the paper.",
        feedback="This is detailed feedback.",
    )


def _overview() -> OverviewFeedback:
    return OverviewFeedback(
        summary="",
        issues=[OverviewIssue(title="Issue", body="Body")],
    )


def test_detect_section_focus_routes_common_section_types():
    assert (
        _detect_section_focus(
            SectionInfo(number=1, title="Methods", text="x", section_type=SectionType.METHODOLOGY)
        )
        == "methodology"
    )
    assert (
        _detect_section_focus(
            SectionInfo(
                number=1,
                title="Discussion",
                text="x",
                section_type=SectionType.DISCUSSION,
            )
        )
        == "discussion"
    )
    assert (
        _detect_section_focus(
            SectionInfo(
                number=1,
                title="Proof",
                text="x" * 600,
                section_type=SectionType.OTHER,
                math_content=True,
            )
        )
        == "proof"
    )


def test_review_section_chains_verify_for_proof_sections():
    section_agent = Mock()
    verify_agent = Mock()
    first_pass = [_comment(1)]
    verified = [_comment(2)]
    section_agent.run.return_value = first_pass
    verify_agent.run.return_value = verified
    section = SectionInfo(
        number=1,
        title="Proof",
        text="x" * 600,
        section_type=SectionType.OTHER,
        math_content=True,
    )

    result = _review_section(
        section_agent,
        verify_agent,
        section,
        "Paper",
        _overview(),
        None,
        "proof",
        "",
        [section],
        "Abstract",
    )

    assert result == verified
    section_agent.run.assert_called_once()
    verify_agent.run.assert_called_once()


def test_run_editorial_pass_falls_back_to_crossref_and_critique():
    with (
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
    ):
        MockEditorial.return_value.run.side_effect = RuntimeError("boom")
        crossref_comments = [_comment(10)]
        critique_comments = [_comment(11)]
        MockCrossref.return_value.run.return_value = crossref_comments
        MockCritique.return_value.run.return_value = critique_comments

        result = run_editorial_pass(
            Mock(),
            "paper text",
            _overview(),
            [_comment(1)],
            title="Paper",
            abstract="Abstract",
            author_notes="please focus on identification",
        )

    assert result == critique_comments
    MockCrossref.return_value.run.assert_called_once()
    MockCritique.return_value.run.assert_called_once()
