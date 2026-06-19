"""Tests for src/coarse/lang_eval.py — cross-language consistency harness.

Pure-function coverage (no LLM): quote_fidelity (programmatic), the recommend
heuristic, the ground-truth adapter, and compare_languages wiring with the
semantic-recall judge monkeypatched. The live driver (scripts/lang_eval_run.py)
is not exercised here — it makes paid review_paper calls (maintainer-run only).
"""

from __future__ import annotations

from coarse import lang_eval
from coarse.lang_eval import (
    LanguageConsistency,
    _to_ground_truth,
    compare_languages,
    format_report,
    quote_fidelity,
    recommend,
)
from coarse.recall import GroundTruthComment, RecallReport
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, Review

_PAPER = (
    "# A Paper\n\n"
    "The estimator is consistent under assumption two as shown in Section 3.\n\n"
    "We assume the errors are independent and identically distributed throughout.\n\n"
    "The simulation results confirm the asymptotic theory developed above.\n"
)


def _comment(n: int, quote: str) -> DetailedComment:
    return DetailedComment(number=n, title=f"Comment {n}", quote=quote, feedback="Feedback.")


def _review(comments: list[DetailedComment]) -> Review:
    return Review(
        title="A Paper",
        domain="x",
        taxonomy="y",
        date="06/18/2026",
        overall_feedback=OverviewFeedback(issues=[OverviewIssue(title="I", body="B")]),
        detailed_comments=comments,
    )


def _recall(semantic: float) -> RecallReport:
    return RecallReport(
        location_recall=0.0,
        semantic_recall=semantic,
        precision=0.0,
        f1=0.0,
        n_ground_truth=0,
        n_generated=0,
        matched_pairs=[],
        unmatched_gt=[],
        unmatched_pred=[],
    )


# --- quote_fidelity (programmatic, real) ---


def test_quote_fidelity_all_verified():
    comments = [
        _comment(1, "The estimator is consistent under assumption two as shown in Section 3."),
        _comment(2, "We assume the errors are independent and identically distributed throughout."),
    ]
    assert quote_fidelity(comments, _PAPER) == 1.0


def test_quote_fidelity_partial():
    comments = [
        _comment(1, "The estimator is consistent under assumption two as shown in Section 3."),
        _comment(2, "This sentence is nowhere to be found in the source paper text at all."),
    ]
    assert quote_fidelity(comments, _PAPER) == 0.5


def test_quote_fidelity_empty_is_vacuously_one():
    assert quote_fidelity([], _PAPER) == 1.0


# --- recommend heuristic (pure) ---


def _result(overlap: float, en_fid: float, loc_fid: float) -> LanguageConsistency:
    return LanguageConsistency(
        language="Spanish",
        n_english=10,
        n_localized=10,
        issue_overlap=overlap,
        reverse_overlap=overlap,
        english_quote_fidelity=en_fid,
        localized_quote_fidelity=loc_fid,
    )


def test_recommend_sufficient():
    verdict = recommend(_result(0.85, 0.98, 0.97))
    assert "SUFFICIENT" in verdict
    assert "Spanish" in verdict


def test_recommend_flags_low_overlap():
    verdict = recommend(_result(0.50, 0.98, 0.97))
    assert "CONSIDER English-pivot" in verdict
    assert "overlap" in verdict


def test_recommend_flags_low_fidelity():
    verdict = recommend(_result(0.85, 0.98, 0.80))
    assert "CONSIDER English-pivot" in verdict
    assert "fidelity" in verdict


def test_recommend_flags_fidelity_gap_even_when_absolute_ok():
    # localized fidelity 0.93 clears the 0.90 floor but trails English (1.00) by >5pp
    verdict = recommend(_result(0.85, 1.00, 0.93))
    assert "CONSIDER English-pivot" in verdict
    assert "trails English" in verdict


def test_recommend_thresholds_are_tunable():
    # An overlap that fails the default passes a lower custom threshold.
    r = _result(0.55, 0.98, 0.97)
    assert "CONSIDER" in recommend(r)
    assert "SUFFICIENT" in recommend(r, consistency_threshold=0.5)


# --- adapter ---


def test_to_ground_truth_preserves_fields():
    gt = _to_ground_truth([_comment(3, "A sufficiently long verbatim quote here.")])
    assert gt[0] == GroundTruthComment(
        index=3,
        title="Comment 3",
        quote="A sufficiently long verbatim quote here.",
        feedback_text="Feedback.",
    )


# --- compare_languages wiring (recall judge mocked) ---


def test_compare_languages_builds_report(monkeypatch):
    monkeypatch.setattr(lang_eval, "compute_recall", lambda *a, **k: _recall(0.8))
    english = _review(
        [
            _comment(1, "The estimator is consistent under assumption two as shown in Section 3."),
            _comment(
                2, "We assume the errors are independent and identically distributed throughout."
            ),
        ]
    )
    # Localized review: one verbatim (source-language) quote present, one absent.
    localized = _review(
        [
            _comment(1, "The simulation results confirm the asymptotic theory developed above."),
            _comment(2, "Esta cita no aparece en el documento original en ninguna parte."),
        ]
    )
    report = compare_languages(
        english, {"Spanish": localized}, _PAPER, client=None, paper="paper.pdf"
    )
    assert len(report.results) == 1
    r = report.results[0]
    assert r.language == "Spanish"
    assert r.issue_overlap == 0.8
    assert r.reverse_overlap == 0.8
    assert r.n_english == 2 and r.n_localized == 2
    assert r.english_quote_fidelity == 1.0  # both english quotes are in the paper
    assert r.localized_quote_fidelity == 0.5  # one of two localized quotes verifies
    assert len(report.recommendations) == 1
    # overlap 0.8 ok but localized fidelity 0.5 → flagged
    assert "CONSIDER English-pivot" in report.recommendations[0]


def test_format_report_renders_language_and_verdict(monkeypatch):
    monkeypatch.setattr(lang_eval, "compute_recall", lambda *a, **k: _recall(0.9))
    english = _review([_comment(1, "The estimator is consistent under assumption two as shown.")])
    localized = _review([_comment(1, "The estimator is consistent under assumption two as shown.")])
    report = compare_languages(english, {"French": localized}, _PAPER, client=None, paper="p")
    text = format_report(report)
    assert "French" in text
    assert "Verdict" in text
    assert "consistency" in text or "overlap" in text
