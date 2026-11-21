"""Run refutation on a review already scored, and cross-tabulate the results.

The `pipeline_refuted` arm was a separate pipeline run, so comparing it with
the `pipeline` arm compares two different reviews and cannot attribute the
difference to refutation. This applies the refuter to the exact comments the
judge already adjudicated, so each comment contributes one paired observation:
did the refuter drop the comments the judge called unsupported, and did it keep
the ones the judge called supported?

Usage:
    OPENROUTER_API_KEY=... uv run python evals/refute_saved.py \
        --run evals/runs/psi__pipeline__run2
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from coarse.agent.refutation import refute_comments, refute_issues
from coarse.config import load_config
from coarse.llm import LLMClient
from coarse.types import PaperStructure, Review

logging.basicConfig(level=logging.WARNING)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--model", default="openrouter/anthropic/claude-opus-5.5")
    ap.add_argument(
        "--save-review",
        action="store_true",
        help="Write the post-refutation review as its own run, for scoring.",
    )
    args = ap.parse_args()

    meta = json.loads((args.run / "meta.json").read_text())
    paper_dir = Path("evals/papers") / meta["paper"]
    review = Review.model_validate_json((args.run / "review.json").read_text())
    structure = PaperStructure.model_validate_json((paper_dir / "structure.json").read_text())
    paper = (paper_dir / "paper.md").read_text()
    score = json.loads((args.run / "score.json").read_text())

    judged = {
        d["number"]: d
        for d in score["precision"]["detail"]
        if d.get("kind") == "comment" and d.get("verdict") in {"supported", "unsupported"}
    }

    client = LLMClient(model=args.model, config=load_config())
    kept, verdicts, records = refute_comments(review.detailed_comments, paper, structure, client)
    kept_numbers = {c.number for c in kept}
    verdict_by_number = {int(v.finding_id.lstrip("c")): v for v in verdicts}

    # Paired table: judge verdict against refuter action, per comment.
    cells = {
        ("supported", "kept"): 0,
        ("supported", "dropped"): 0,
        ("unsupported", "kept"): 0,
        ("unsupported", "dropped"): 0,
    }
    rows = []
    for comment in review.detailed_comments:
        j = judged.get(comment.number)
        if j is None:
            continue
        action = "kept" if comment.number in kept_numbers else "dropped"
        cells[(j["verdict"], action)] += 1
        v = verdict_by_number.get(comment.number)
        rows.append(
            {
                "number": comment.number,
                "title": comment.title,
                "judge": j["verdict"],
                "refuter": v.verdict if v else "no-verdict",
                "action": action,
            }
        )

    # Same paired treatment for the macro issues: the judge already adjudicated
    # them (kind == "issue", numbered 1000 + position), so each issue is one
    # paired observation of whether refutation narrowed or dropped the ones the
    # judge called unsupported.
    judged_issues = {
        d["number"] - 1000: d
        for d in score["precision"]["detail"]
        if d.get("kind") == "issue" and d.get("verdict") in {"supported", "unsupported"}
    }
    kept_issues, issue_verdicts, issue_records = refute_issues(
        review.overall_feedback.issues, paper, structure, client
    )
    verdict_by_index = {v.issue_index: v for v in issue_verdicts}
    issue_cells: dict[tuple[str, str], int] = {}
    issue_rows = []
    for i, issue in enumerate(review.overall_feedback.issues, start=1):
        j = judged_issues.get(i)
        if j is None:
            continue
        v = verdict_by_index.get(i)
        outcome = (
            "dropped"
            if v is not None and v.verdict == "refuted"
            else "narrowed"
            if v is not None and v.verdict == "partly_supported" and v.rewritten_body.strip()
            else "kept"
        )
        issue_cells[(j["verdict"], outcome)] = issue_cells.get((j["verdict"], outcome), 0) + 1
        issue_rows.append(
            {
                "index": i,
                "title": issue.title,
                "judge": j["verdict"],
                "refuter": v.verdict if v else "no-verdict",
                "outcome": outcome,
            }
        )

    # Persist the post-refutation review as its own run so it can be scored on
    # the same footing as any arm. Generation is identical to the input run, so
    # a precision comparison between the two is paired on generation and
    # isolates the gate — including whether a narrowed issue is actually better
    # than the one it replaced, which the paired table above cannot show
    # because the narrowed text is new and unjudged.
    if args.save_review:
        from coarse.synthesis import render_review

        verified = review.model_copy(
            update={
                "overall_feedback": review.overall_feedback.model_copy(
                    update={"issues": kept_issues}
                ),
                "detailed_comments": [
                    c.model_copy(update={"number": i}) for i, c in enumerate(kept, start=1)
                ],
            }
        )
        out_dir = args.run.parent / f"{meta['paper']}__pipeline_refuted_paired__run{meta['run']}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "review.json").write_text(verified.model_dump_json(indent=1), encoding="utf-8")
        (out_dir / "review.md").write_text(render_review(verified), encoding="utf-8")
        (out_dir / "meta.json").write_text(
            json.dumps(
                {
                    **meta,
                    "arm": "pipeline_refuted_paired",
                    "cost_usd": round(client.cost_usd, 2),
                    "comments_before_quote_verify": len(kept),
                    "comments_after_quote_verify": len(kept),
                    "quote_drop_rate": 0.0,
                    "n_overall_issues": len(kept_issues),
                    "refuted_from": str(args.run),
                    "agents": [],
                },
                indent=1,
            ),
            encoding="utf-8",
        )
        print(f"\n  saved post-refutation review to {out_dir}")

    out = {
        "run": str(args.run),
        "issues": {
            "n_issues": len(review.overall_feedback.issues),
            "n_judged": len(judged_issues),
            "n_kept": len(kept_issues),
            "paired": {f"judge_{k[0]}__{k[1]}": v for k, v in issue_cells.items()},
            "n_refuter_agents": len(issue_records),
            "rows": issue_rows,
        },
        "model": client.model,
        "n_comments": len(review.detailed_comments),
        "n_judged": len(judged),
        "n_kept": len(kept_numbers),
        "paired": {f"judge_{k[0]}__{k[1]}": v for k, v in cells.items()},
        "refutation_cost_usd": round(client.cost_usd, 2),
        "n_refuter_agents": len(records),
        "rows": rows,
    }
    (args.run / "refute_paired.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\n{meta['paper']} {meta['arm']} run{meta['run']} — paired refutation")
    print(
        f"  comments: {len(review.detailed_comments)}, judged: {len(judged)}, "
        f"kept by refuter: {len(kept_numbers)}"
    )
    print(f"  refutation cost: ${client.cost_usd:.2f} over {len(records)} agents\n")
    print(f"  {'':22} {'refuter kept':>13} {'refuter dropped':>16}")
    for jv in ("supported", "unsupported"):
        print(f"  judge {jv:16} {cells[(jv, 'kept')]:>13} {cells[(jv, 'dropped')]:>16}")
    tp = cells[("unsupported", "dropped")]
    fp = cells[("supported", "dropped")]
    print(
        f"\n  of the comments the judge called unsupported, refutation dropped "
        f"{tp}/{tp + cells[('unsupported', 'kept')]}"
    )
    print(
        f"  of the comments the judge called supported, refutation dropped "
        f"{fp}/{fp + cells[('supported', 'kept')]} (collateral)"
    )
    print("\n  macro issues")
    print(
        f"    issues: {len(review.overall_feedback.issues)}, judged: {len(judged_issues)}, "
        f"kept by refuter: {len(kept_issues)}"
    )
    print(f"    {'':22} {'kept':>8} {'narrowed':>10} {'dropped':>9}")
    for jv in ("supported", "unsupported"):
        print(
            f"    judge {jv:16} "
            f"{issue_cells.get((jv, 'kept'), 0):>8} "
            f"{issue_cells.get((jv, 'narrowed'), 0):>10} "
            f"{issue_cells.get((jv, 'dropped'), 0):>9}"
        )
    print(f"\n  wrote {args.run / 'refute_paired.json'}")


if __name__ == "__main__":
    main()
