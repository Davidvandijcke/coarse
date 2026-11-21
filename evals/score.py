"""Score a review against an atomized reference, and adjudicate its precision.

Two measurements, deliberately separate:

**Recall** — for each reference finding, did the review surface it? Matching is
by judge, because the same defect is written very differently by two referees
("the gradient has the opposite sign" vs "the displayed derivative disagrees
with Algorithm 5"), and string overlap misses that.

**Precision** — for each comment the review emitted, is it supported by the
paper? This is judged against the paper itself, never against the reference.
The reference reviews available here are partial, so a comment that does not
match one is not thereby wrong; treating absence as error would score a correct
new finding as a false positive. This is also the measurement that matters most:
the pipeline's known failure mode is a confident wrong critique, and recall
alone rewards volume.

The judge is a different model family from the reviewer under test, so a model
is never grading its own prose.
"""

from __future__ import annotations

import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from coarse.llm import LLMClient
from coarse.types import Review

logger = logging.getLogger(__name__)

# Cross-family judge: the arms under test run on Claude, so the judge is GPT.
JUDGE_MODEL = "openrouter/openai/gpt-5.6-terra-pro"

# Comments beyond this rank are not scored, so an arm cannot buy recall by
# emitting more (#270 AC-3).
DEFAULT_TOP_K = 20


class _MatchVerdict(BaseModel):
    matched_comment: int = Field(
        default=0,
        description="Number of the comment that covers the reference finding, or 0 if none does.",
    )
    reasoning: str = Field(default="", description="One or two sentences.")


class _SupportVerdict(BaseModel):
    verdict: Literal["supported", "unsupported", "unclear"] = Field(
        description=(
            "supported: the paper really has this defect and the comment describes it "
            "accurately. unsupported: the paper does not have it, or the comment misreads "
            "the paper, or it is pure speculation. unclear: cannot tell from the paper."
        )
    )
    substantive: bool = Field(
        default=True,
        description=(
            "False if the comment is cosmetic, a request for extra work, or a restatement "
            "of something the paper already says, rather than a defect."
        ),
    )
    reasoning: str = Field(default="", description="One or two sentences citing the paper.")


def _render_comments(review: Review, top_k: int) -> str:
    parts = []
    for c in review.detailed_comments[:top_k]:
        parts.append(
            f"[comment {c.number}] ({c.severity}) {c.title}\n"
            f"  quote: {c.quote[:600]}\n"
            f"  feedback: {c.feedback[:1800]}"
        )
    for i, issue in enumerate(review.overall_feedback.issues, start=1001):
        parts.append(f"[comment {i}] (overall) {issue.title}\n  feedback: {issue.body[:1800]}")
    return "\n\n".join(parts) if parts else "(the review contains no comments)"


def score_recall(
    review: Review,
    reference: dict,
    client: LLMClient,
    *,
    top_k: int = DEFAULT_TOP_K,
    max_parallel: int = 6,
) -> dict:
    """Which reference findings did this review surface?"""
    rendered = _render_comments(review, top_k)
    findings = reference["findings"]

    def judge(finding: dict) -> dict:
        task = (
            "A reference referee report on a paper contains the finding below. Another "
            "review of the same paper is also given. Decide whether any comment in that "
            "other review identifies the SAME underlying defect. Wording will differ; "
            "judge the substance. A comment that merely touches the same section without "
            "identifying the same defect does NOT match.\n\n"
            f"REFERENCE FINDING\nLocation: {finding['location']}\n{finding['claim']}\n\n"
            f"THE OTHER REVIEW\n{rendered}\n\n"
            "Return the matching comment number, or 0 if none matches."
        )
        try:
            out = client.complete(
                [
                    {
                        "role": "system",
                        "content": (
                            "You match peer-review findings across two reports. You are "
                            "strict: a match requires the same defect, not the same topic."
                        ),
                    },
                    {"role": "user", "content": task},
                ],
                _MatchVerdict,
                max_tokens=2048,
                temperature=0.0,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("recall judge failed on %s: %s", finding["id"], exc)
            return {"id": finding["id"], "matched": False, "error": str(exc)}
        return {
            "id": finding["id"],
            "importance": finding.get("importance", ""),
            "tags": finding.get("tags", []),
            "matched": out.matched_comment != 0,
            "matched_comment": out.matched_comment,
            "reasoning": out.reasoning,
        }

    with ThreadPoolExecutor(max_workers=max_parallel) as pool:
        results = list(pool.map(judge, findings))

    hits = [r for r in results if r.get("matched")]
    via_issue = [r for r in hits if r.get("matched_comment", 0) >= 1001]
    via_comment = [r for r in hits if 0 < r.get("matched_comment", 0) < 1001]
    return {
        "n_reference_findings": len(findings),
        "n_matched": len(hits),
        "recall": len(hits) / len(findings) if findings else 0.0,
        "n_matched_via_detailed_comment": len(via_comment),
        "n_matched_via_overall_issue": len(via_issue),
        "recall_detailed_only": (len(via_comment) / len(findings) if findings else 0.0),
        "matched_ids": sorted(r["id"] for r in hits),
        "missed_ids": sorted(r["id"] for r in results if not r.get("matched")),
        "detail": results,
    }


class _Claim(BaseModel):
    """One adjudicable unit of a review: a detailed comment or a macro issue."""

    number: int
    kind: Literal["comment", "issue"]
    title: str
    quote: str = ""
    feedback: str
    severity: str = "major"


def review_claims(review: Review, top_k: int = DEFAULT_TOP_K) -> list[_Claim]:
    """Everything in a review that asserts something about the paper.

    Both halves are included. Scoring only the detailed comments made the
    measurement asymmetric: recall credited a macro issue for finding a
    reference defect while precision never audited one, so an arm that put its
    claims in the overall feedback was credited for hits and never charged for
    misses. On the benchmark paper the whole of one arm's recall came from its
    macro issues.
    """
    claims = [
        _Claim(
            number=c.number,
            kind="comment",
            title=c.title,
            quote=c.quote,
            feedback=c.feedback,
            severity=c.severity,
        )
        for c in review.detailed_comments[:top_k]
    ]
    claims += [
        _Claim(
            number=1000 + i,
            kind="issue",
            title=issue.title,
            feedback=issue.body,
        )
        for i, issue in enumerate(review.overall_feedback.issues, start=1)
    ]
    return claims


def score_precision(
    review: Review,
    paper_markdown: str,
    client: LLMClient,
    *,
    top_k: int = DEFAULT_TOP_K,
    max_parallel: int = 6,
) -> dict:
    """Is each claim the review makes actually supported by the paper?"""
    comments = review_claims(review, top_k)

    def judge(comment) -> dict:
        task = (
            "Below is the full text of a paper, then one item from a referee report on "
            "it. Decide whether the paper really has the defect the item describes.\n\n"
            "Check the comment against the paper directly. Look up any definition, lemma, "
            "algorithm or equation the comment refers to. A comment is 'unsupported' if the "
            "paper does not have the defect, if the comment misreads the paper, if it "
            "contradicts something the paper proves, or if it asserts an error without the "
            "paper containing one. Do not be charitable about plausible-sounding but "
            "incorrect mathematics.\n\n"
            f"PAPER\n{paper_markdown}\n\n"
            f"{'MACRO ISSUE' if comment.kind == 'issue' else 'DETAILED COMMENT'}\n"
            f"Title: {comment.title}\nSeverity: {comment.severity}\n"
            + (f"Quote: {comment.quote}\n" if comment.quote else "")
            + f"Feedback: {comment.feedback}"
        )
        try:
            out = client.complete(
                [
                    {
                        "role": "system",
                        "content": (
                            "You audit peer-review comments for correctness against the "
                            "paper. You are an expert in mathematics and statistics. Your "
                            "job is to catch confident but wrong criticism."
                        ),
                    },
                    {"role": "user", "content": task},
                ],
                _SupportVerdict,
                max_tokens=3072,
                temperature=0.0,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("precision judge failed on comment %s: %s", comment.number, exc)
            return {
                "number": comment.number,
                "kind": comment.kind,
                "verdict": "error",
                "error": str(exc),
            }
        return {
            "number": comment.number,
            "kind": comment.kind,
            "title": comment.title,
            "severity": comment.severity,
            "verdict": out.verdict,
            "substantive": out.substantive,
            "reasoning": out.reasoning,
        }

    if not comments:
        return {"n_comments": 0, "precision": None, "detail": []}

    with ThreadPoolExecutor(max_workers=max_parallel) as pool:
        results = list(pool.map(judge, comments))

    scored = [r for r in results if r.get("verdict") in {"supported", "unsupported", "unclear"}]
    supported = [r for r in scored if r["verdict"] == "supported"]
    unsupported = [r for r in scored if r["verdict"] == "unsupported"]
    substantive_supported = [r for r in supported if r.get("substantive")]
    by_kind = {}
    for kind in ("comment", "issue"):
        of_kind = [r for r in scored if r.get("kind") == kind]
        sup = [r for r in of_kind if r["verdict"] == "supported"]
        by_kind[kind] = {
            "n": len(of_kind),
            "n_supported": len(sup),
            "n_unsupported": sum(1 for r in of_kind if r["verdict"] == "unsupported"),
            "precision": (len(sup) / len(of_kind)) if of_kind else None,
        }
    return {
        "n_claims": len(comments),
        "n_comments": sum(1 for c in comments if c.kind == "comment"),
        "n_issues": sum(1 for c in comments if c.kind == "issue"),
        "by_kind": by_kind,
        "n_scored": len(scored),
        "n_supported": len(supported),
        "n_unsupported": len(unsupported),
        "n_unclear": len(scored) - len(supported) - len(unsupported),
        "precision": len(supported) / len(scored) if scored else None,
        "substantive_precision": (len(substantive_supported) / len(scored) if scored else None),
        "detail": results,
    }


def judge_client() -> LLMClient:
    from coarse.config import load_config

    return LLMClient(model=JUDGE_MODEL, config=load_config())


def score_run(
    review_path: Path,
    reference_path: Path,
    paper_path: Path,
    *,
    top_k: int = DEFAULT_TOP_K,
) -> dict:
    """Score one saved review. Returns the combined report."""
    review = Review.model_validate_json(review_path.read_text(encoding="utf-8"))
    reference = json.loads(reference_path.read_text(encoding="utf-8"))
    paper = paper_path.read_text(encoding="utf-8")
    client = judge_client()
    recall = score_recall(review, reference, client, top_k=top_k)
    precision = score_precision(review, paper, client, top_k=top_k)
    return {
        "review": str(review_path),
        "judge_model": client.model,
        "top_k": top_k,
        "n_detailed_comments": len(review.detailed_comments),
        "n_overall_issues": len(review.overall_feedback.issues),
        "recall": recall,
        "precision": precision,
        "judge_cost_usd": round(client.cost_usd, 4),
    }
