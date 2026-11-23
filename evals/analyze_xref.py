"""Analyse the paired cross-reference A/B exactly as preregistered.

Reads `evals/PREREGISTRATION_xref.md`'s decision rule and applies it to the
matched pairs: each `agent_swarm_xref` run and its `agent_swarm_r1` twin, which
share a plan, a first pass and a set of round-1 verdicts.

Usage:
    uv run python evals/analyze_xref.py
"""

from __future__ import annotations

import json
from pathlib import Path

RUNS = Path("evals/runs")
# Preregistered thresholds. Changing these after the runs is the failure mode
# the preregistration exists to prevent.
SHIP_MIN_MEAN_RECALL_GAIN = 1.0
SHIP_MIN_NONNEGATIVE_RUNS = 3
DELETE_BAD_JUMP = 2


def _load(run_dir: Path) -> dict | None:
    score = run_dir / "score.json"
    if not score.is_file():
        return None
    d = json.loads(score.read_text())
    prec = d["precision"]
    substantive = sum(
        1 for x in prec["detail"] if x.get("verdict") == "supported" and x.get("substantive", True)
    )
    scored = sum(1 for x in prec["detail"] if x.get("verdict") in {"supported", "unsupported"})
    return {
        "recall": d["recall"]["n_matched"],
        "matched": sorted(d["recall"]["matched_ids"]),
        "n_claims": scored,
        "good": substantive,
        "bad": scored - substantive,
        "precision": prec.get("precision"),
    }


def main() -> None:
    pairs = []
    for xref_dir in sorted(RUNS.glob("psi__agent_swarm_xref__run*")):
        run = xref_dir.name.rsplit("run", 1)[1]
        r1_dir = RUNS / f"psi__agent_swarm_r1__run{run}"
        if not r1_dir.is_dir():
            continue
        a, b = _load(r1_dir), _load(xref_dir)
        if a is None or b is None:
            continue
        pairs.append((run, a, b))

    if not pairs:
        print("no scored pairs yet")
        return

    print(f"\n{len(pairs)} matched pair(s) — arm A = round 1 only, arm B = rounds 1+2\n")
    header = (
        f"{'run':>4}  {'recall A':>8} {'recall B':>8} {'d':>4}   "
        f"{'bad A':>6} {'bad B':>6} {'d':>4}   {'good A':>7} {'good B':>7}"
    )
    print(header)
    print("-" * len(header))
    d_recall, d_bad = [], []
    for run, a, b in pairs:
        dr = b["recall"] - a["recall"]
        db = b["bad"] - a["bad"]
        d_recall.append(dr)
        d_bad.append(db)
        print(
            f"{run:>4}  {a['recall']:>8} {b['recall']:>8} {dr:>+4}   "
            f"{a['bad']:>6} {b['bad']:>6} {db:>+4}   {a['good']:>7} {b['good']:>7}"
        )

    mean_dr = sum(d_recall) / len(d_recall)
    mean_db = sum(d_bad) / len(d_bad)
    nonneg = sum(1 for x in d_recall if x >= 0)
    print(f"\nmean d_recall {mean_dr:+.2f} findings   (of 16)")
    print(f"mean d_bad    {mean_db:+.2f} claims")
    print(f"runs with d_recall >= 0: {nonneg}/{len(d_recall)}")
    print(f"runs with d_bad >= +{DELETE_BAD_JUMP}: {sum(1 for x in d_bad if x >= DELETE_BAD_JUMP)}")

    ship = (
        mean_dr >= SHIP_MIN_MEAN_RECALL_GAIN
        and nonneg >= SHIP_MIN_NONNEGATIVE_RUNS
        and mean_db <= 0
        and not any(x >= DELETE_BAD_JUMP for x in d_bad)
    )
    delete = mean_dr <= 0 or sum(1 for x in d_bad if x >= DELETE_BAD_JUMP) >= 2
    verdict = (
        "SHIP (rounds=2 default)"
        if ship
        else "DELETE"
        if delete
        else "LEAVE AS IS (off by default)"
    )
    print(f"\npreregistered verdict: {verdict}")
    if ship and delete:
        print("  (both branches matched — report the conflict, do not pick)")

    out = {
        "n_pairs": len(pairs),
        "d_recall": d_recall,
        "d_bad": d_bad,
        "mean_d_recall": mean_dr,
        "mean_d_bad": mean_db,
        "verdict": verdict,
        "pairs": [{"run": r, "arm_a": a, "arm_b": b} for r, a, b in pairs],
    }
    Path("evals/runs/xref_analysis.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nwrote evals/runs/xref_analysis.json")


if __name__ == "__main__":
    main()
