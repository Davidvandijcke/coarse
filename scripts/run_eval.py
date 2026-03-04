"""Run Phase 2 eval: review all 5 reference papers and score against references.

Usage: uv run python scripts/run_eval.py [--model MODEL] [--cheap]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from coarse.llm import LLMClient
from coarse.pipeline import review_paper
from coarse.quality import evaluate_review_panel
from coarse.synthesis import render_review

DATA_DIR = Path(__file__).parent.parent / "data" / "refine_examples"

# Papers with their PDF paths and reference review paths
PAPERS = {
    "r3d": {
        "pdf": DATA_DIR / "r3d" / "r3d (16).pdf",
        "reference": DATA_DIR / "r3d" / "feedback-regression-discontinuity-design-with-distribution--2026-03-03.md",
    },
    "targeting_interventions": {
        "pdf": DATA_DIR / "targeting_interventions" / "paper.pdf",
        "reference": DATA_DIR / "targeting_interventions" / "reference_review.md",
    },
    "cortical_circuits": {
        "pdf": DATA_DIR / "cortical_circuits" / "paper.pdf",
        "reference": DATA_DIR / "cortical_circuits" / "reference_review.md",
    },
    "coset_codes": {
        "pdf": DATA_DIR / "coset_codes" / "paper.pdf",
        "reference": DATA_DIR / "coset_codes" / "reference_review.md",
    },
    "population_genetics": {
        "pdf": DATA_DIR / "population_genetics" / "paper.pdf",
        "reference": DATA_DIR / "population_genetics" / "reference_review.md",
    },
}


def run_paper(name: str, info: dict, model: str) -> dict:
    """Run pipeline on one paper, return results dict."""
    pdf_path = info["pdf"]
    ref_path = info["reference"]

    if not pdf_path.exists():
        return {"name": name, "error": f"PDF not found: {pdf_path}"}

    print(f"\n{'='*60}")
    print(f"  Reviewing: {name}")
    print(f"{'='*60}")

    t0 = time.time()
    try:
        review, markdown = review_paper(
            pdf_path, model=model, skip_cost_gate=True,
        )
    except Exception as e:
        return {"name": name, "error": str(e), "elapsed_s": time.time() - t0}

    elapsed = time.time() - t0
    print(f"  Done in {elapsed:.1f}s — {len(review.overall_feedback.issues)} issues, "
          f"{len(review.detailed_comments)} comments")

    # Save the review
    out_dir = pdf_path.parent
    out_path = out_dir / "coarse_review_phase2.md"
    out_path.write_text(markdown, encoding="utf-8")

    result = {
        "name": name,
        "elapsed_s": elapsed,
        "n_issues": len(review.overall_feedback.issues),
        "n_comments": len(review.detailed_comments),
        "domain_detected": review.domain,
        "review_path": str(out_path),
    }

    # Score against reference if available
    if ref_path and ref_path.exists():
        print(f"  Scoring against reference...")
        reference = ref_path.read_text(encoding="utf-8")
        eval_client = LLMClient(model=model)
        try:
            synth_report, individual = evaluate_review_panel(
                markdown, reference, client=eval_client,
                paper_text=review.title,  # lightweight context
            )
            result["scores"] = {
                "overall": synth_report.overall_score,
                "dimensions": {
                    d.dimension: {"score": d.score, "reasoning": d.reasoning}
                    for d in synth_report.dimensions
                },
                "strengths": synth_report.strengths,
                "weaknesses": synth_report.weaknesses,
            }
            print(f"  Score: {synth_report.overall_score:.1f}/5.0")
            for d in synth_report.dimensions:
                print(f"    {d.dimension}: {d.score}/5")
        except Exception as e:
            result["eval_error"] = str(e)
            print(f"  Eval failed: {e}")
    else:
        print(f"  No reference review — skipping scoring")

    return result


def main():
    parser = argparse.ArgumentParser(description="Run Phase 2 eval on 5 reference papers")
    parser.add_argument("--model", default=None, help="Model to use (default: from config)")
    parser.add_argument("--cheap", action="store_true", help="Use cheap model")
    parser.add_argument("--paper", type=str, default=None, help="Run only one paper (by name)")
    args = parser.parse_args()

    if args.cheap:
        model = "openrouter/google/gemini-2.5-flash"
    else:
        model = args.model  # None → review_paper uses config.default_model

    print(f"Phase 2 Eval — Model: {model}")
    print(f"Papers: {', '.join(PAPERS.keys())}")

    papers_to_run = PAPERS
    if args.paper:
        if args.paper not in PAPERS:
            print(f"Unknown paper: {args.paper}. Available: {', '.join(PAPERS.keys())}")
            sys.exit(1)
        papers_to_run = {args.paper: PAPERS[args.paper]}

    results = []
    for name, info in papers_to_run.items():
        result = run_paper(name, info, model)
        results.append(result)

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    for r in results:
        if "error" in r:
            print(f"  {r['name']}: ERROR — {r['error']}")
        elif "scores" in r:
            print(f"  {r['name']}: {r['scores']['overall']:.1f}/5.0 "
                  f"({r['n_issues']} issues, {r['n_comments']} comments, {r['elapsed_s']:.0f}s)")
        else:
            print(f"  {r['name']}: no reference ({r['n_issues']} issues, "
                  f"{r['n_comments']} comments, {r['elapsed_s']:.0f}s)")

    # Save results
    out_path = Path(__file__).parent.parent / "data" / "phase2_eval_results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Convert Path objects for JSON serialization
    serializable = []
    for r in results:
        sr = {k: (str(v) if isinstance(v, Path) else v) for k, v in r.items()}
        serializable.append(sr)
    out_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
