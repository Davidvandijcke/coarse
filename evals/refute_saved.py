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

from coarse.agent.orchestrator import refute_comments
from coarse.config import load_config
from coarse.llm import LLMClient
from coarse.types import PaperStructure, Review

logging.basicConfig(level=logging.WARNING)


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

    out = {
        "run": str(args.run),
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
    print(f"\n  wrote {args.run / 'refute_paired.json'}")


if __name__ == "__main__":
    main()
