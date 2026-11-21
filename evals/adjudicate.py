"""Re-adjudicate a saved run with a judge that can read the paper and compute.

Checks the central claim of docs/AGENTIC_REVIEW.md -- that the staged
pipeline's unsupported comments are objections the paper answers elsewhere --
with a judge that has the means to look, rather than one answering from a
single prompt.

Usage:
    OPENROUTER_API_KEY=... uv run python evals/adjudicate.py \
        --run evals/runs/psi__pipeline__run1 [--limit 12]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from score import judge_client, score_precision_with_tools  # noqa: E402

from coarse.types import PaperStructure, Review  # noqa: E402

logging.basicConfig(level=logging.WARNING)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    meta = json.loads((args.run / "meta.json").read_text())
    paper_dir = Path("evals/papers") / meta["paper"]
    review = Review.model_validate_json((args.run / "review.json").read_text())
    structure = PaperStructure.model_validate_json((paper_dir / "structure.json").read_text())
    paper = (paper_dir / "paper.md").read_text()

    client = judge_client()
    report = score_precision_with_tools(review, paper, structure, client, limit=args.limit)
    report["meta"] = meta
    out = args.run / "score_tool_judge.json"
    out.write_text(json.dumps(report, indent=1), encoding="utf-8")

    print(f"\n{meta['arm']} run{meta['run']} — tool-using adjudication")
    print(f"  claims adjudicated : {report['n_scored']} of {report['n_claims']}")
    print(f"  supported          : {report['n_supported']}")
    print(f"  unsupported        : {report['n_unsupported']}")
    print(
        f"     ... because answered elsewhere in the paper: "
        f"{report['n_unsupported_because_answered_elsewhere']}"
    )
    print(f"  unclear            : {report['n_unclear']}")
    p = report["precision"]
    print(f"  precision          : {p:.0%}" if p is not None else "  precision : n/a")
    print(f"\n  wrote {out}")
    print("\n  unsupported claims:")
    for d in report["detail"]:
        if d.get("verdict") != "unsupported":
            continue
        tag = f" [answered in {d['where']}]" if d.get("answered_elsewhere") else ""
        print(f"    [{d.get('severity', '?')}] {d.get('title', '')[:66]}{tag}")
        print(f"        {d.get('reasoning', '')[:200]}")


if __name__ == "__main__":
    main()
