"""Score every saved run under evals/runs and print a comparison table.

Usage:
    OPENROUTER_API_KEY=... uv run python evals/score_runs.py [--only arm1,arm2]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from score import DEFAULT_TOP_K, score_run

logging.basicConfig(level=logging.WARNING)

RUNS = Path("evals/runs")
REFERENCES = Path("evals/references")
PAPERS = Path("evals/papers")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="Comma-separated arm names to score.")
    ap.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    ap.add_argument("--force", action="store_true", help="Rescore runs that already have a score.")
    args = ap.parse_args()
    wanted = {a for a in args.only.split(",") if a}

    rows = []
    for run_dir in sorted(RUNS.iterdir()):
        meta_path = run_dir / "meta.json"
        review_path = run_dir / "review.json"
        if not meta_path.is_file() or not review_path.is_file():
            continue
        meta = json.loads(meta_path.read_text())
        if wanted and meta["arm"] not in wanted:
            continue

        score_path = run_dir / "score.json"
        if score_path.is_file() and not args.force:
            report = json.loads(score_path.read_text())
        else:
            print(f"scoring {run_dir.name} ...", flush=True)
            report = score_run(
                review_path,
                REFERENCES / f"{meta['paper']}.json",
                PAPERS / meta["paper"] / "paper.md",
                top_k=args.top_k,
            )
            report["meta"] = meta
            score_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
        rows.append((meta, report))

    if not rows:
        print("nothing to score")
        return

    print()
    header = (
        f"{'arm':14} {'run':>3} {'cmts':>5} {'recall':>7} {'hits':>7} "
        f"{'prec':>6} {'unsup':>6} {'cost$':>7} {'secs':>6}"
    )
    print(header)
    print("-" * len(header))
    for meta, report in sorted(rows, key=lambda r: (r[0]["arm"], r[0]["run"])):
        rec = report["recall"]
        prec = report["precision"]
        p = prec.get("precision")
        print(
            f"{meta['arm']:14} {meta['run']:>3} "
            f"{report['n_detailed_comments']:>5} "
            f"{rec['recall']:>6.0%} "
            f"{rec['n_matched']:>3}/{rec['n_reference_findings']:<3} "
            f"{(f'{p:.0%}' if p is not None else '  n/a'):>6} "
            f"{prec.get('n_unsupported', 0):>6} "
            f"{meta['cost_usd']:>7.2f} {meta['elapsed_s']:>6.0f}"
        )

    print("\nreference findings matched, by arm:")
    for meta, report in sorted(rows, key=lambda r: (r[0]["arm"], r[0]["run"])):
        ids = report["recall"]["matched_ids"]
        print(f"  {meta['arm']:14} run{meta['run']}  {', '.join(ids) or '(none)'}")

    print("\nunsupported comments flagged by the adjudicator:")
    for meta, report in sorted(rows, key=lambda r: (r[0]["arm"], r[0]["run"])):
        bad = [d for d in report["precision"]["detail"] if d.get("verdict") == "unsupported"]
        if not bad:
            continue
        print(f"  {meta['arm']} run{meta['run']}:")
        for d in bad:
            print(f"    [{d['severity']}] {d['title'][:70]}")
            print(f"        {d['reasoning'][:220]}")


if __name__ == "__main__":
    main()
