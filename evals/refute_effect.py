"""Measure what refutation changes, with judge re-run noise held out.

The gate is subtractive: it drops comments and deletes named spans from issues,
and never rewrites. So every surviving comment carries the verdict already
stored in `score.json` and needs no re-judging, and the only text the judge has
to see again is a narrowed issue body.

Scoring a post-refutation review end to end re-judges every claim, including
the ones refutation left byte-identical. The judge is not deterministic -- on
one run it moved a `psi` review from 13 of 20 supported to 12 of 20 between two
scorings of the same file -- so a before/after precision comparison mixes the
gate's effect with that drift. On the first attempt the drift was large enough
to make the arithmetic impossible: the gate's own actions capped `psi` at 7 of
10 supported issues and the score reported 8.

This script removes the drift. Every claim refutation left unchanged keeps the
verdict already stored in `score.json`; only text the refuter rewrote is sent
to the judge. So each claim is judged once per distinct text, and the
difference between before and after is attributable to three things the script
reports separately: claims dropped, rewritten claims that converted, and
rewritten claims that did not.

Usage:
    OPENROUTER_API_KEY=... uv run python evals/refute_effect.py \
        --run evals/runs/psi__pipeline__run2
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from score import judge_client, score_precision  # noqa: E402

from coarse.agent.refutation import refute_review  # noqa: E402
from coarse.config import load_config  # noqa: E402
from coarse.llm import LLMClient  # noqa: E402
from coarse.types import (  # noqa: E402
    OverviewFeedback,
    PaperStructure,
    Review,
)

logging.basicConfig(level=logging.WARNING)


def _pct(part: int, whole: int) -> str:
    return f"{part / whole:.0%}" if whole else "n/a"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--model", default="openrouter/anthropic/claude-opus-5.5")
    args = ap.parse_args()

    meta = json.loads((args.run / "meta.json").read_text())
    paper_dir = Path("evals/papers") / meta["paper"]
    review = Review.model_validate_json((args.run / "review.json").read_text())
    structure = PaperStructure.model_validate_json((paper_dir / "structure.json").read_text())
    paper = (paper_dir / "paper.md").read_text()
    stored = json.loads((args.run / "score.json").read_text())["precision"]["detail"]

    # The before-set is exactly the claims the judge actually adjudicated.
    # score.json caps detailed comments at top_k, so a review with more
    # comments than the cap has unjudged ones; counting those among the
    # survivors inflated the after-total above the before-total, which is
    # impossible for a gate that only drops and rewrites.
    #
    # Claims are tracked by (kind, title): the gate never alters a title, and
    # titles are unique within a review in practice. Both the verdict and the
    # judge's `substantive` flag are carried forward. "supported" alone was
    # satisfiable by retreating from an error claim to "the paper does not say
    # X" back when the gate rewrote comments; it no longer does, but the
    # distinction is still reported because a narrowed issue can shed its
    # substantive content and keep a defensible remainder.
    before_by_title: dict[tuple[str, str], tuple[str, bool, str]] = {}
    for d in stored:
        if d.get("verdict") not in {"supported", "unsupported"}:
            continue
        kind = d.get("kind", "comment")
        if kind == "comment":
            idx = d["number"] - 1
            source = review.detailed_comments
            text = source[idx].feedback if 0 <= idx < len(source) else None
            title = source[idx].title if 0 <= idx < len(source) else None
        else:
            idx = d["number"] - 1001
            source = review.overall_feedback.issues
            text = source[idx].body if 0 <= idx < len(source) else None
            title = source[idx].title if 0 <= idx < len(source) else None
        if title is None or text is None:
            continue
        before_by_title[(kind, title)] = (
            d["verdict"],
            bool(d.get("substantive", True)),
            text,
        )

    client = LLMClient(model=args.model, config=load_config())
    new_overview, kept_comments, records = refute_review(
        review.overall_feedback, list(review.detailed_comments), paper, structure, client
    )

    survivors: dict[tuple[str, str], str] = {}
    for c in kept_comments:
        survivors[("comment", c.title)] = c.feedback
    for issue in new_overview.issues:
        survivors[("issue", issue.title)] = issue.body

    unchanged: list[tuple[str, str, bool]] = []
    rewritten_comments, rewritten_issues = [], []
    dropped = 0
    for (kind, title), (verdict, substantive, old_text) in before_by_title.items():
        new_text = survivors.get((kind, title))
        if new_text is None:
            dropped += 1
            continue
        if new_text == old_text:
            unchanged.append((kind, verdict, substantive))
            continue
        if kind == "comment":
            match = next(c for c in kept_comments if c.title == title)
            rewritten_comments.append(match)
        else:
            match = next(i for i in new_overview.issues if i.title == title)
            rewritten_issues.append(match)

    judged: list[dict] = []
    if rewritten_comments or rewritten_issues:
        judge = judge_client()
        synthetic = Review(
            title=review.title,
            domain=review.domain,
            taxonomy=review.taxonomy,
            date=datetime.date.today().strftime("%m/%d/%Y"),
            overall_feedback=OverviewFeedback(
                issues=rewritten_issues or review.overall_feedback.issues[:1]
            ),
            detailed_comments=[
                c.model_copy(update={"number": i})
                for i, c in enumerate(rewritten_comments, start=1)
            ],
        )
        report = score_precision(synthetic, paper, judge, top_k=100)
        for d in report["detail"]:
            if d.get("verdict") not in {"supported", "unsupported"}:
                continue
            # When there were no rewritten issues a placeholder was supplied to
            # satisfy the schema; its verdict is not part of this measurement.
            if d.get("kind") == "issue" and not rewritten_issues:
                continue
            judged.append(d)
        judge_cost = judge.cost_usd
    else:
        judge_cost = 0.0

    def tally(kind: str, *, require_substantive: bool) -> tuple[int, int]:
        def good_unchanged(verdict: str, substantive: bool) -> bool:
            return verdict == "supported" and (substantive or not require_substantive)

        sup = sum(1 for k, v, sub in unchanged if k == kind and good_unchanged(v, sub))
        tot = sum(1 for k, _v, _s in unchanged if k == kind)
        sup += sum(
            1
            for d in judged
            if d.get("kind") == kind
            and d["verdict"] == "supported"
            and (d.get("substantive", True) or not require_substantive)
        )
        tot += sum(1 for d in judged if d.get("kind") == kind)
        return sup, tot

    before = {"comment": [0, 0, 0], "issue": [0, 0, 0]}
    for d in stored:
        if d.get("verdict") not in {"supported", "unsupported"}:
            continue
        kind = d.get("kind", "comment")
        before[kind][2] += 1
        if d["verdict"] == "supported":
            before[kind][0] += 1
            if d.get("substantive", True):
                before[kind][1] += 1

    print(f"\n{meta['paper']} {meta['arm']} run{meta['run']} — refutation effect")
    print("  verdicts carried forward for unchanged text; only rewrites re-judged")
    print(
        f"  refutation ${client.cost_usd:.2f} over {len(records)} agents; "
        f"judging ${judge_cost:.2f} for {len(judged)} rewritten claim(s)"
    )
    print(
        f"  {len(unchanged)} claim(s) unchanged, {len(judged)} rewritten, "
        f"{before['comment'][2] + before['issue'][2] - len(unchanged) - len(judged)} dropped\n"
    )

    for label, require in (("supported", False), ("supported AND substantive", True)):
        print(f"  {label}")
        print(f"  {'':10} {'before':>22} {'after':>22}")
        tot_sup_b = tot_sup_a = tot_n_b = tot_n_a = 0
        for kind in ("comment", "issue"):
            sup_a, n_a = tally(kind, require_substantive=require)
            sup_b = before[kind][1] if require else before[kind][0]
            n_b = before[kind][2]
            tot_sup_b += sup_b
            tot_sup_a += sup_a
            tot_n_b += n_b
            tot_n_a += n_a
            print(
                f"  {kind + 's':10} "
                f"{f'{sup_b} good, {n_b - sup_b} bad':>22} "
                f"{f'{sup_a} good, {n_a - sup_a} bad':>22}"
                f"   ({_pct(sup_b, n_b)} -> {_pct(sup_a, n_a)})"
            )
        print(
            f"  {'total':10} "
            f"{f'{tot_sup_b}/{tot_n_b} ({_pct(tot_sup_b, tot_n_b)})':>16} "
            f"{f'{tot_sup_a}/{tot_n_a} ({_pct(tot_sup_a, tot_n_a)})':>16}"
        )
        print(
            f"  {'':10} {'bad: ' + str(tot_n_b - tot_sup_b):>16} "
            f"{'bad: ' + str(tot_n_a - tot_sup_a):>16}\n"
        )

    converted = sum(1 for d in judged if d["verdict"] == "supported")
    hedged = sum(
        1 for d in judged if d["verdict"] == "supported" and not d.get("substantive", True)
    )
    print(
        f"  of {len(judged)} rewritten claims: {converted} judged supported, "
        f"of which {hedged} judged NOT substantive"
    )
    print("  (a rewrite that retreats from an error claim to 'the paper does not say X'")
    print("   passes the supported test and fails the substantive one)")

    out = {
        "run": str(args.run),
        "before": {
            k: {"supported": before[k][0], "substantive": before[k][1], "n": before[k][2]}
            for k in before
        },
        "after": {
            k: {
                "supported": tally(k, require_substantive=False)[0],
                "substantive": tally(k, require_substantive=True)[0],
                "n": tally(k, require_substantive=False)[1],
            }
            for k in ("comment", "issue")
        },
        "n_before_adjudicated": len(before_by_title),
        "n_dropped": dropped,
        "n_unchanged": len(unchanged),
        "n_rewritten_judged": len(judged),
        "n_rewritten_supported": converted,
        "n_rewritten_supported_but_not_substantive": hedged,
        "refutation_cost_usd": round(client.cost_usd, 2),
        "judge_cost_usd": round(judge_cost, 2),
        "rewritten_detail": judged,
        "actions": [
            {
                "kind": kind,
                "title": title,
                "judge_before": before_by_title[(kind, title)][0],
                "substantive_before": before_by_title[(kind, title)][1],
                "action": (
                    "dropped"
                    if (kind, title) not in survivors
                    else "unchanged"
                    if survivors[(kind, title)] == before_by_title[(kind, title)][2]
                    else "narrowed"
                ),
            }
            for (kind, title) in before_by_title
        ],
    }
    # Save the narrowed text and the refuter's records. 15 of 35 issues across
    # the benchmark papers were narrowed and nothing was persisting what they
    # now say, so no one could read a deletion-narrowed issue for dangling
    # fragments or a lost antecedent.
    review_after = review.model_copy(
        update={
            "overall_feedback": new_overview,
            "detailed_comments": [
                c.model_copy(update={"number": i}) for i, c in enumerate(kept_comments, start=1)
            ],
        }
    )
    (args.run / "review_after_refutation.json").write_text(
        review_after.model_dump_json(indent=1), encoding="utf-8"
    )
    from coarse.synthesis import render_review

    (args.run / "review_after_refutation.md").write_text(
        render_review(review_after), encoding="utf-8"
    )
    out["narrowed_issues"] = [
        {
            "title": issue.title,
            "before": before_by_title[("issue", issue.title)][2],
            "after": issue.body,
        }
        for issue in new_overview.issues
        if ("issue", issue.title) in before_by_title
        and before_by_title[("issue", issue.title)][2] != issue.body
    ]
    (args.run / "refute_effect.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\n  wrote {args.run / 'refute_effect.json'}")


if __name__ == "__main__":
    main()
