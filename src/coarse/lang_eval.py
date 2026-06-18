"""Cross-language review-consistency evaluation (dev-only).

Answers PR-F of the multilingual rollout (``docs/MULTILINGUAL_PLAN.md``): does
writing the review *directly* in a non-English language (design A, the shipped
generation-time localization) change **which issues** the reviewer finds,
compared to writing it in English? If the same paper yields the same issues in
language X as in English, and the quotes still verify, then design A is not
degrading the analysis and the heavier English-pivot design (B / PR-G —
review in English, then translate the output) is unnecessary. If issue overlap
drops or quotes stop verifying for some language, that is the evidence that
would justify building B for that language.

Method (deliberately judge-light, reusing existing eval infra):

  * **Issue overlap** — ``recall.compute_recall`` with the *English-baseline*
    review's comments as the "ground truth" and the language-X review's
    comments as the "generated" set. Its semantic LLM judge matches issues
    across languages, so ``semantic_recall`` = the fraction of English-found
    issues that the language-X review also found. We also run it in reverse
    (English as generated vs X as truth) to catch issues X found that English
    missed.
  * **Quote fidelity** — programmatic (``quote_verify``): the fraction of a
    review's comments whose quotes verify verbatim against the source paper.
    Localization must never alter quotes (they stay in the paper's language),
    so a fidelity drop in language X is a direct red flag.

The metric/aggregation/recommendation functions below are pure and unit-tested,
and (like ``quality.py`` / ``recall.py``) this module operates on already-
produced ``Review`` objects — it deliberately does NOT import the pipeline. The
*live* driver that actually runs ``review_paper`` once per language (i.e. makes
**paid LLM calls**) lives in ``scripts/lang_eval_run.py`` and is meant to be run
manually by a maintainer with API keys and a chosen set of papers; it is never
invoked from the pipeline or CI.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from coarse.llm import LLMClient
from coarse.models import QUALITY_MODEL
from coarse.quote_verify import verify_quotes
from coarse.recall import GroundTruthComment, compute_recall
from coarse.types import DetailedComment, Review

logger = logging.getLogger(__name__)

# Defaults for the recommendation heuristic. A language passes ("design A is
# sufficient") only if its review found most of the issues the English review
# found AND its quotes verify at near-English rates. Tuned to be permissive on
# overlap (cross-language semantic matching is noisy) but strict on fidelity
# (a quote that no longer verifies is an unambiguous defect).
DEFAULT_CONSISTENCY_THRESHOLD = 0.70
DEFAULT_FIDELITY_THRESHOLD = 0.90


def _to_ground_truth(comments: list[DetailedComment]) -> list[GroundTruthComment]:
    """Adapt a Review's comments into the GroundTruthComment shape compute_recall
    accepts as its ``reference`` argument."""
    return [
        GroundTruthComment(
            index=c.number,
            title=c.title,
            quote=c.quote,
            feedback_text=c.feedback,
        )
        for c in comments
    ]


def quote_fidelity(comments: list[DetailedComment], paper_markdown: str) -> float:
    """Fraction of comments whose quotes verify verbatim against the paper.

    1.0 when every quote is found (or there are no comments — vacuously fine);
    lower values mean localization (or extraction) broke the quote anchor.
    Uses the same programmatic verifier the pipeline uses.
    """
    if not comments:
        return 1.0
    verified = verify_quotes(comments, paper_markdown, drop_unverified=True)
    return len(verified) / len(comments)


class LanguageConsistency(BaseModel):
    """Consistency metrics for one non-English review vs the English baseline."""

    language: str = Field(description="Review-output language name or code")
    n_english: int = Field(description="Comment count in the English baseline review")
    n_localized: int = Field(description="Comment count in the localized review")
    issue_overlap: float = Field(
        description=(
            "Fraction of English-baseline issues also found by the localized "
            "review (semantic_recall, cross-language judge)"
        ),
    )
    reverse_overlap: float = Field(
        description="Fraction of localized issues also present in the English baseline",
    )
    english_quote_fidelity: float = Field(
        description="Quote-verify rate of the English baseline review",
    )
    localized_quote_fidelity: float = Field(
        description="Quote-verify rate of the localized review",
    )


class LangEvalReport(BaseModel):
    """Per-paper cross-language consistency report + a policy recommendation."""

    paper: str = Field(description="Paper identifier (path or title)")
    results: list[LanguageConsistency]
    recommendations: list[str] = Field(
        description="Per-language verdict lines (design A sufficient vs consider English-pivot)",
    )
    consistency_threshold: float = DEFAULT_CONSISTENCY_THRESHOLD
    fidelity_threshold: float = DEFAULT_FIDELITY_THRESHOLD


def recommend(
    result: LanguageConsistency,
    *,
    consistency_threshold: float = DEFAULT_CONSISTENCY_THRESHOLD,
    fidelity_threshold: float = DEFAULT_FIDELITY_THRESHOLD,
) -> str:
    """Return a one-line verdict for a language's consistency result.

    Design A is judged sufficient for the language iff issue overlap clears the
    consistency threshold AND the localized review's quote fidelity neither
    falls below the fidelity threshold nor materially trails the English
    baseline (>5 percentage points). Otherwise the line flags the specific
    failure as evidence for the English-pivot design (B / PR-G).
    """
    reasons: list[str] = []
    ok = True
    if result.issue_overlap < consistency_threshold:
        ok = False
        reasons.append(
            f"issue overlap {result.issue_overlap:.0%} < {consistency_threshold:.0%} "
            f"(direct-in-language review found fewer of the English-baseline issues)"
        )
    fidelity_gap = result.english_quote_fidelity - result.localized_quote_fidelity
    if result.localized_quote_fidelity < fidelity_threshold:
        ok = False
        reasons.append(
            f"quote fidelity {result.localized_quote_fidelity:.0%} < {fidelity_threshold:.0%}"
        )
    elif fidelity_gap > 0.05:
        ok = False
        reasons.append(
            f"quote fidelity trails English by {fidelity_gap:.0%} "
            f"({result.localized_quote_fidelity:.0%} vs {result.english_quote_fidelity:.0%})"
        )
    if ok:
        return (
            f"{result.language}: design A SUFFICIENT — overlap {result.issue_overlap:.0%}, "
            f"fidelity {result.localized_quote_fidelity:.0%}."
        )
    return f"{result.language}: CONSIDER English-pivot — " + "; ".join(reasons) + "."


def compare_languages(
    english_review: Review,
    localized_reviews: dict[str, Review],
    paper_markdown: str,
    *,
    client: LLMClient | None = None,
    model: str = QUALITY_MODEL,
    paper: str = "",
    consistency_threshold: float = DEFAULT_CONSISTENCY_THRESHOLD,
    fidelity_threshold: float = DEFAULT_FIDELITY_THRESHOLD,
) -> LangEvalReport:
    """Compare each localized review against the English baseline for one paper.

    Pure-ish: the only external calls are the semantic recall judge (one per
    direction per language). Quote fidelity is programmatic. Returns a report
    with per-language metrics and a recommendation line each.
    """
    english_gt = _to_ground_truth(english_review.detailed_comments)
    english_fid = quote_fidelity(english_review.detailed_comments, paper_markdown)

    results: list[LanguageConsistency] = []
    for language, review in localized_reviews.items():
        forward = compute_recall(
            review.detailed_comments, english_gt, client=client, model=model
        )
        reverse = compute_recall(
            english_review.detailed_comments,
            _to_ground_truth(review.detailed_comments),
            client=client,
            model=model,
        )
        results.append(
            LanguageConsistency(
                language=language,
                n_english=len(english_review.detailed_comments),
                n_localized=len(review.detailed_comments),
                issue_overlap=forward.semantic_recall,
                reverse_overlap=reverse.semantic_recall,
                english_quote_fidelity=english_fid,
                localized_quote_fidelity=quote_fidelity(
                    review.detailed_comments, paper_markdown
                ),
            )
        )

    recommendations = [
        recommend(
            r,
            consistency_threshold=consistency_threshold,
            fidelity_threshold=fidelity_threshold,
        )
        for r in results
    ]
    return LangEvalReport(
        paper=paper,
        results=results,
        recommendations=recommendations,
        consistency_threshold=consistency_threshold,
        fidelity_threshold=fidelity_threshold,
    )


def format_report(report: LangEvalReport) -> str:
    """Render a LangEvalReport as a human-readable text block."""
    lines = [
        f"# Cross-language review consistency — {report.paper or '(paper)'}",
        "",
        f"Thresholds: issue-overlap ≥ {report.consistency_threshold:.0%}, "
        f"quote-fidelity ≥ {report.fidelity_threshold:.0%}",
        "",
        f"{'language':<22} {'overlap':>8} {'reverse':>8} {'fidelity':>9} {'(en fid)':>9}  comments",
    ]
    for r in report.results:
        lines.append(
            f"{r.language:<22} {r.issue_overlap:>7.0%} {r.reverse_overlap:>7.0%} "
            f"{r.localized_quote_fidelity:>8.0%} {r.english_quote_fidelity:>8.0%}  "
            f"{r.n_localized} vs {r.n_english} (en)"
        )
    lines.append("")
    lines.append("## Verdict")
    lines.extend(f"- {line}" for line in report.recommendations)
    return "\n".join(lines)
