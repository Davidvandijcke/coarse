"""Tests for coarse.quality — evaluate_review and QualityReport."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.llm import LLMClient
from coarse.models import QUALITY_MODEL
from coarse.quality import DimensionScore, QualityReport, _JudgeOutput, evaluate_review, save_quality_report
from coarse.synthesis import render_review
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, Review


def _make_dimension(dimension: str, score: float) -> DimensionScore:
    return DimensionScore(dimension=dimension, score=score, reasoning=f"Reasoning for {dimension}.")


def _make_judge_output(scores: list[float]) -> _JudgeOutput:
    dimensions = [
        _make_dimension(dim, score)
        for dim, score in zip(["coverage", "specificity", "depth", "format"], scores)
    ]
    return _JudgeOutput(
        dimensions=dimensions,
        strengths=["Strong point A", "Strong point B"],
        weaknesses=["Weak point A", "Weak point B"],
    )


def _make_mock_client(scores: list[float]) -> LLMClient:
    client = MagicMock(spec=LLMClient)
    client.complete.return_value = _make_judge_output(scores)
    return client


def _make_review() -> Review:
    return Review(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="3/3/2026",
        overall_feedback=OverviewFeedback(
            issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}.") for i in range(1, 5)]
        ),
        detailed_comments=[
            DetailedComment(
                number=1,
                title="Comment One",
                quote="Some verbatim text from the paper.",
                feedback="Some actionable feedback.",
            )
        ],
    )


def test_evaluate_review_with_string_inputs():
    """Pass two short markdown strings; mock client; assert overall_score equals mean of dimension scores."""
    scores = [3, 4, 3, 5]
    client = _make_mock_client(scores)

    result = evaluate_review(
        generated="# Generated Review\n\nSome review content.",
        reference="# Reference Review\n\nReference content.",
        client=client,
    )

    assert isinstance(result, QualityReport)
    expected_mean = sum(scores) / len(scores)
    assert result.overall_score == pytest.approx(expected_mean)
    assert len(result.dimensions) == 4
    assert len(result.strengths) == 2
    assert len(result.weaknesses) == 2


def test_evaluate_review_with_review_object():
    """Pass a Review object; verify it is rendered via render_review before being sent to LLM."""
    scores = [4, 4, 4, 4]
    client = _make_mock_client(scores)

    review = _make_review()
    rendered = render_review(review)

    evaluate_review(generated=review, reference="# Reference\n\nContent.", client=client)

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_msg = next(m for m in messages if m["role"] == "user")

    assert rendered in user_msg["content"]


def test_overall_score_is_mean_of_dimensions():
    """Construct QualityReport directly and assert overall_score equals arithmetic mean."""
    dimensions = [
        DimensionScore(dimension="coverage", score=2, reasoning="Low."),
        DimensionScore(dimension="specificity", score=4, reasoning="Good."),
        DimensionScore(dimension="depth", score=3, reasoning="Average."),
        DimensionScore(dimension="format", score=5, reasoning="Perfect."),
    ]
    expected_mean = (2 + 4 + 3 + 5) / 4  # 3.5

    report = QualityReport(
        overall_score=expected_mean,
        dimensions=dimensions,
        strengths=["S1", "S2"],
        weaknesses=["W1", "W2"],
    )

    assert report.overall_score == pytest.approx(expected_mean)
    assert report.overall_score == pytest.approx(3.5)


def test_evaluate_review_creates_default_client():
    """Call evaluate_review without a client; confirm default LLMClient is created."""
    scores = [3, 3, 3, 3]

    with patch("coarse.quality.LLMClient") as mock_cls:
        mock_instance = MagicMock(spec=LLMClient)
        mock_instance.complete.return_value = _make_judge_output(scores)
        mock_cls.return_value = mock_instance

        evaluate_review(
            generated="# Generated\n\nContent.",
            reference="# Reference\n\nContent.",
        )

        mock_cls.assert_called_once_with(model=QUALITY_MODEL)


def test_dimension_scores_in_valid_range():
    """After mocked evaluate_review, assert all DimensionScore.score values in [1,5] and overall_score in [1.0, 5.0]."""
    scores = [2, 3, 4, 5]
    client = _make_mock_client(scores)

    result = evaluate_review(
        generated="# Gen\n\nContent.",
        reference="# Ref\n\nContent.",
        client=client,
    )

    for dim in result.dimensions:
        assert 1 <= dim.score <= 5

    assert 1.0 <= result.overall_score <= 5.0


# ---------------------------------------------------------------------------
# test_save_quality_report_creates_file
# ---------------------------------------------------------------------------

def test_save_quality_report_creates_file(tmp_path):
    """save_quality_report writes a markdown file with expected metadata fields."""
    dimensions = [
        DimensionScore(dimension="coverage", score=4.0, reasoning="Good coverage."),
        DimensionScore(dimension="specificity", score=3.5, reasoning="Some vague points."),
        DimensionScore(dimension="depth", score=4.5, reasoning="Very thorough."),
        DimensionScore(dimension="format", score=5.0, reasoning="Perfect structure."),
    ]
    report = QualityReport(
        overall_score=4.25,
        dimensions=dimensions,
        strengths=["Catches the key assumptions issue"],
        weaknesses=["Misses one minor exposition gap"],
    )

    out = tmp_path / "paper_quality_test.md"
    ref_path = "/data/refine_examples/r3d/reference.md"

    save_quality_report(report, out, ref_path, model=QUALITY_MODEL, mode="single")

    assert out.exists()
    content = out.read_text(encoding="utf-8")

    assert "# Quality Evaluation" in content
    assert ref_path in content
    assert QUALITY_MODEL in content
    assert "single" in content
    assert "4.25/5.0" in content
    assert "coverage" in content
    assert "Catches the key assumptions issue" in content
    assert "Misses one minor exposition gap" in content


def test_save_quality_report_panel_mode(tmp_path):
    """save_quality_report records mode=panel when using panel evaluation."""
    dimensions = [DimensionScore(dimension="coverage", score=3.0, reasoning="OK.")]
    report = QualityReport(overall_score=3.0, dimensions=dimensions, strengths=[], weaknesses=[])

    out = tmp_path / "quality_panel.md"
    save_quality_report(report, out, "/ref.md", mode="panel")

    content = out.read_text(encoding="utf-8")
    assert "panel" in content
