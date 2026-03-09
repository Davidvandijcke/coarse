"""Batch review runner: generates reviews + quality evals with proper labeling.

Usage:
    uv run python scripts/batch_review.py
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coarse.config import load_config
from coarse.llm import LLMClient
from coarse.pipeline import review_paper
from coarse.quality import evaluate_review, save_quality_report

BASE = Path(__file__).parent.parent / "data" / "refine_examples"
JUDGE_MODEL = "gemini/gemini-3.1-pro-preview"
TODAY = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

PAPERS = {
    "cortical_circuits": {
        "pdf": BASE / "cortical_circuits" / "paper.pdf",
        "ref": BASE / "cortical_circuits" / "reference_review_stanford.md",
    },
    "coset_codes": {
        "pdf": BASE / "coset_codes" / "paper.pdf",
        "ref": BASE / "coset_codes" / "reference_review_stanford.md",
    },
    "population_genetics": {
        "pdf": BASE / "population_genetics" / "paper.pdf",
        "ref": BASE / "population_genetics" / "reference_review_stanford.md",
    },
    "targeting_interventions": {
        "pdf": BASE / "targeting_interventions" / "paper.pdf",
        "ref": BASE / "targeting_interventions" / "reference_review_stanford.md",
    },
}


def run_review(paper_name: str, model: str, model_label: str) -> tuple[str, float, str]:
    """Run a single review and return (review_path, cost_usd, review_markdown)."""
    info = PAPERS[paper_name]
    config = load_config()
    config.use_coding_agents = False  # non-agentic

    print(f"\n{'='*60}")
    print(f"Reviewing {paper_name} with {model_label} ({model})")
    print(f"{'='*60}")

    review, markdown, paper_text = review_paper(
        info["pdf"], model=model, skip_cost_gate=True, config=config,
    )

    # Save review
    out_dir = BASE / paper_name
    review_path = out_dir / f"review_{model_label}_{TODAY}.md"
    review_path.write_text(markdown, encoding="utf-8")
    print(f"  Review saved: {review_path.name}")

    # Get cost from client (approximate — pipeline creates its own client)
    # We'll estimate from token counts in the review
    return str(review_path), 0.0, markdown


def run_quality_eval(
    paper_name: str, review_path: str, model_label: str, paper_text_md: str = "",
) -> dict:
    """Run quality eval and save report. Returns scores dict."""
    info = PAPERS[paper_name]
    ref_text = info["ref"].read_text(encoding="utf-8")
    review_text = Path(review_path).read_text(encoding="utf-8")

    # Load paper text for quote verification
    if not paper_text_md:
        # Extract paper text
        from coarse.extraction import extract_text
        pt = extract_text(info["pdf"])
        paper_text_md = pt.full_markdown

    print(f"  Evaluating quality with {JUDGE_MODEL}...")
    client = LLMClient(model=JUDGE_MODEL)
    report = evaluate_review(
        review_text, ref_text, client=client,
        paper_text=paper_text_md, model=JUDGE_MODEL,
    )

    # Save quality report
    out_dir = BASE / paper_name
    quality_path = out_dir / f"paper_quality_{model_label}_{TODAY}.md"
    save_quality_report(report, quality_path, str(info["ref"]), model=JUDGE_MODEL)
    print(f"  Quality saved: {quality_path.name}")
    print(f"  Overall: {report.overall_score:.2f}/6.0")
    for d in report.dimensions:
        print(f"    {d.dimension}: {d.score}")

    return {
        "paper": paper_name,
        "model": model_label,
        "overall": report.overall_score,
        "dimensions": {d.dimension: d.score for d in report.dimensions},
        "judge_cost": client.cost_usd,
    }


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "qwen/qwen3.5-plus-02-15"
    model_label = sys.argv[2] if len(sys.argv) > 2 else "qwen35plus"

    # Only run specific papers if specified
    paper_names = sys.argv[3:] if len(sys.argv) > 3 else list(PAPERS.keys())

    results = []
    for paper_name in paper_names:
        if paper_name not in PAPERS:
            print(f"Unknown paper: {paper_name}, skipping")
            continue

        review_path, cost, markdown = run_review(paper_name, model, model_label)
        scores = run_quality_eval(paper_name, review_path, model_label)
        scores["review_cost"] = cost
        results.append(scores)

    # Summary table
    print(f"\n{'='*80}")
    print(f"SUMMARY: {model_label} ({model}) — judged by {JUDGE_MODEL}")
    print(f"{'='*80}")
    print(f"{'Paper':<25} {'Overall':>8} {'Coverage':>9} {'Specific':>9} {'Depth':>7} {'Format':>8}")
    print("-" * 80)
    for r in results:
        d = r["dimensions"]
        print(
            f"{r['paper']:<25} {r['overall']:>7.2f} "
            f"{d.get('coverage', 0):>8.1f} {d.get('specificity', 0):>8.1f} "
            f"{d.get('depth', 0):>6.1f} {d.get('format', 0):>7.1f}"
        )


if __name__ == "__main__":
    main()
