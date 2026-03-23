"""Tests for recall.py — recall-based evaluation against ground-truth reviews."""
from __future__ import annotations

from unittest.mock import MagicMock

from coarse.recall import (
    GroundTruthComment,
    MatchPair,
    RecallReport,
    _jaccard,
    _tokenize,
    compute_recall,
    location_match,
    parse_plain_review,
    parse_refine_review,
    parse_review_auto,
    save_recall_report,
)
from coarse.types import DetailedComment  # noqa: I001

# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------

_REFINE_MD = """\
# Paper Title

**Date**: 03/03/2026
**Domain**: test
**Taxonomy**: test
**Filter**: Active comments

---

## Overall Feedback

Some overall feedback.

**Status**: [Pending]

---

## Detailed Comments (3)

### 1. First comment title

**Status**: [Pending]

**Quote**:
> This is the verbatim quote from the paper for comment one.

**Feedback**:
This is the feedback for comment one explaining the issue.

---

### 2. Second comment title

**Status**: [Pending]

**Quote**:
> Another verbatim quote from a different section.

**Feedback**:
Feedback for the second comment with details.

---

### 3. Third comment no quote

**Status**: [Pending]

**Quote**:
> Third quote text here.

**Feedback**:
Third comment feedback.
"""


def test_parse_refine_review():
    comments = parse_refine_review(_REFINE_MD)
    assert len(comments) == 3
    assert comments[0].index == 1
    assert comments[0].title == "First comment title"
    assert "verbatim quote" in comments[0].quote
    assert "feedback for comment one" in comments[0].feedback_text


def test_parse_refine_review_empty():
    assert parse_refine_review("No comments here.") == []


_PLAIN_MD = """\
# Comments

1. Validation of the Effective Coding Gain Heuristic: The comparison of code \
performance relies heavily on the rule of thumb that a factor of two increase \
in the error coefficient corresponds to a 0.2 dB loss. I recommend including \
a rigorous validation of this heuristic.

2. Dependency of Complexity Metric on Implementation: The normalized decoding \
complexity metric is defined based on specific trellis-based decoding algorithms. \
To support the generality of the classification, I suggest the authors discuss \
how the ranking might change with alternative decoding architectures.

3. Short.
"""


def test_parse_plain_review():
    comments = parse_plain_review(_PLAIN_MD)
    # Item 3 is too short (<50 chars), should be skipped
    assert len(comments) == 2
    assert comments[0].index == 1
    assert "Validation" in comments[0].title
    assert "rigorous validation" in comments[0].feedback_text


def test_parse_plain_review_empty():
    assert parse_plain_review("No numbered items.") == []


def test_parse_review_auto_refine():
    comments = parse_review_auto(_REFINE_MD)
    assert len(comments) == 3
    assert comments[0].title == "First comment title"


def test_parse_review_auto_plain():
    comments = parse_review_auto(_PLAIN_MD)
    assert len(comments) == 2


# ---------------------------------------------------------------------------
# Matching tests
# ---------------------------------------------------------------------------

def _gt(index: int, quote: str = "", feedback: str = "feedback") -> GroundTruthComment:
    return GroundTruthComment(
        index=index, title=f"GT {index}", quote=quote, feedback_text=feedback,
    )


def _pred(
    number: int,
    quote: str = "a sufficiently long placeholder quote text for testing",
    feedback: str = "some generic test feedback content",
) -> DetailedComment:
    return DetailedComment(
        number=number, title=f"Pred {number}",
        quote=quote,
        feedback=feedback,
    )


def test_tokenize():
    tokens = _tokenize("Hello world! This is a test.")
    assert "hello" in tokens
    assert "world" in tokens


def test_jaccard_identical():
    s = {"a", "b", "c"}
    assert _jaccard(s, s) == 1.0


def test_jaccard_disjoint():
    assert _jaccard({"a", "b"}, {"c", "d"}) == 0.0


def test_jaccard_partial():
    assert 0.0 < _jaccard({"a", "b", "c"}, {"b", "c", "d"}) < 1.0


def test_jaccard_empty():
    assert _jaccard(set(), {"a"}) == 0.0


def test_location_match_same_quote():
    gt = _gt(1, quote="the minimum distance between two distinct paths is at least three")
    pred = _pred(1, quote="the minimum distance between two distinct paths is at least three times")
    assert location_match(gt, pred)


def test_location_match_different_quotes():
    gt = _gt(
        1,
        quote="convergence rate of the estimator under regularity conditions",
        feedback="the convergence proof has a gap in step three",
    )
    pred = _pred(
        1,
        quote="completely unrelated text about a different topic entirely",
        feedback="the table values do not match the theoretical predictions",
    )
    assert not location_match(gt, pred)


def test_location_match_no_quote_uses_feedback():
    gt = _gt(1, quote="", feedback="the error coefficient heuristic needs validation")
    pred = _pred(
        1,
        quote="the error coefficient heuristic approximation rule of thumb",
        feedback="the error coefficient heuristic should be validated rigorously",
    )
    assert location_match(gt, pred)


# ---------------------------------------------------------------------------
# Recall computation tests
# ---------------------------------------------------------------------------

def test_compute_recall_perfect():
    """All ground-truth comments matched."""
    gt = [
        _gt(1, quote="shared quote text about error"),
        _gt(2, quote="another shared passage"),
    ]
    gen = [
        _pred(1, quote="shared quote text about error"),
        _pred(2, quote="another shared passage"),
    ]

    report = compute_recall(gen, gt, client=MagicMock())
    assert report.location_recall == 1.0
    assert report.n_ground_truth == 2
    assert report.n_generated == 2


def test_compute_recall_none():
    """No matches."""
    gt = [_gt(
        1,
        quote="convergence rate of the maximum likelihood estimator",
        feedback="the proof of theorem three has a fundamental gap",
    )]
    gen = [_pred(
        1,
        quote="the table entries for experiment seven are inconsistent",
        feedback="numerical values in table seven do not match equation twelve",
    )]

    # Mock client that always says NO
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.answer = "NO"
    mock_client.complete.return_value = mock_result

    report = compute_recall(gen, gt, client=mock_client)
    assert report.location_recall == 0.0
    assert report.semantic_recall == 0.0
    assert len(report.unmatched_gt) == 1


def test_compute_recall_empty_reference():
    report = compute_recall([_pred(1)], [], client=MagicMock())
    assert report.location_recall == 0.0
    assert report.n_ground_truth == 0


def test_compute_recall_from_markdown():
    """Can accept markdown strings and parse them."""
    report = compute_recall(_REFINE_MD, _REFINE_MD, client=MagicMock())
    # Same review compared to itself should have perfect location recall
    assert report.location_recall == 1.0


# ---------------------------------------------------------------------------
# Report persistence tests
# ---------------------------------------------------------------------------

def test_save_recall_report(tmp_path):
    report = RecallReport(
        location_recall=0.5, semantic_recall=0.75, precision=0.6, f1=0.667,
        n_ground_truth=4, n_generated=5,
        matched_pairs=[MatchPair(gt_index=1, pred_number=1, match_type="location")],
        unmatched_gt=[2, 3], unmatched_pred=[4, 5],
    )
    out = tmp_path / "recall.md"
    save_recall_report(report, out, "ref.md", "gen.md")
    content = out.read_text()
    assert "50.0%" in content
    assert "75.0%" in content
    assert "ref.md" in content


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

def test_ground_truth_comment_model():
    c = GroundTruthComment(index=1, feedback_text="test")
    assert c.index == 1
    assert c.quote == ""
    assert c.title == ""


def test_recall_report_model():
    r = RecallReport(
        location_recall=0.5, semantic_recall=0.5, precision=0.5, f1=0.5,
        n_ground_truth=2, n_generated=2,
        matched_pairs=[], unmatched_gt=[], unmatched_pred=[],
    )
    assert r.f1 == 0.5
