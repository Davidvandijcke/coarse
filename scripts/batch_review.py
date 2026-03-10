"""Batch review runner: generates reviews + quality evals against all references.

Usage:
    uv run python scripts/batch_review.py <model_id> <model_label> [paper_names...]

Examples:
    uv run python scripts/batch_review.py "anthropic/claude-sonnet-4-6" "sonnet46"
    uv run python scripts/batch_review.py "qwen/qwen3.5-plus-02-15" "qwen35plus" coset_codes
    uv run python scripts/batch_review.py "moonshotai/kimi-k2.5" "kimik25"
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coarse.config import load_config
from coarse.extraction import extract_text
from coarse.llm import LLMClient
from coarse.pipeline import review_paper
from coarse.quality import evaluate_review, save_quality_report

BASE = Path(__file__).parent.parent / "data" / "refine_examples"
JUDGE_MODEL = "gemini/gemini-3.1-pro-preview"
TODAY = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Paper PDFs
PAPERS = {
    "cortical_circuits": BASE / "cortical_circuits" / "paper.pdf",
    "coset_codes": BASE / "coset_codes" / "paper.pdf",
    "population_genetics": BASE / "population_genetics" / "paper.pdf",
    "targeting_interventions": BASE / "targeting_interventions" / "paper.pdf",
}

# References per paper: {paper: {ref_id: path}}
REFS: dict[str, dict[str, Path]] = {
    "cortical_circuits": {
        "refine": BASE / "cortical_circuits" / "reference_review.md",
        "stanford": BASE / "cortical_circuits" / "reference_review_stanford.md",
        "reviewer3": BASE / "cortical_circuits" / "review_reviewer3.md",
    },
    "coset_codes": {
        "refine": BASE / "coset_codes" / "reference_review.md",
        "stanford": BASE / "coset_codes" / "reference_review_stanford.md",
        "reviewer3": BASE / "coset_codes" / "review_reviewer3.md",
    },
    "population_genetics": {
        "refine": BASE / "population_genetics" / "reference_review.md",
        "stanford": BASE / "population_genetics" / "reference_review_stanford.md",
        "reviewer3": BASE / "population_genetics" / "review_reviewer3.md",
    },
    "targeting_interventions": {
        "refine": BASE / "targeting_interventions" / "reference_review.md",
        "stanford": BASE / "targeting_interventions" / "reference_review_stanford.md",
        "reviewer3": BASE / "targeting_interventions" / "reviewer3_review.md",
    },
}


def run_review(paper_name: str, model: str, model_label: str) -> tuple[str, str, str]:
    """Run review, return (review_path, review_markdown, paper_text_markdown)."""
    pdf_path = PAPERS[paper_name]
    config = load_config()

    print(f"\n{'='*60}")
    print(f"REVIEW: {paper_name} with {model_label} ({model})")
    print(f"{'='*60}")

    review, markdown, paper_text = review_paper(
        pdf_path, model=model, skip_cost_gate=True, config=config,
    )

    out_dir = BASE / paper_name
    review_path = out_dir / f"review_{model_label}_{TODAY}.md"
    review_path.write_text(markdown, encoding="utf-8")
    print(f"  Review saved: {review_path.name}")

    return str(review_path), markdown, paper_text.full_markdown


def run_quality_evals(
    paper_name: str,
    review_markdown: str,
    model_label: str,
    paper_text_md: str,
) -> list[dict]:
    """Run quality eval against all 3 references for one paper/model combo."""
    refs = REFS[paper_name]
    results = []

    for ref_id, ref_path in refs.items():
        if not ref_path.exists():
            print(f"  SKIP quality vs {ref_id}: {ref_path.name} not found")
            continue

        ref_text = ref_path.read_text(encoding="utf-8")
        quality_filename = f"quality_{model_label}_vs_{ref_id}_{TODAY}.md"
        quality_path = BASE / paper_name / quality_filename

        print(f"  Quality vs {ref_id} ({JUDGE_MODEL})...")
        client = LLMClient(model=JUDGE_MODEL)
        report = evaluate_review(
            review_markdown, ref_text, client=client,
            paper_text=paper_text_md, model=JUDGE_MODEL,
        )

        save_quality_report(report, quality_path, str(ref_path), model=JUDGE_MODEL)
        print(f"    Saved: {quality_filename}")
        print(f"    Overall: {report.overall_score:.2f}/6.0")
        for d in report.dimensions:
            print(f"      {d.dimension}: {d.score}")

        results.append({
            "ref": ref_id,
            "overall": report.overall_score,
            "dimensions": {d.dimension: d.score for d in report.dimensions},
            "cost": client.cost_usd,
        })

    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: uv run python scripts/batch_review.py <model_id> <model_label> [paper_names...]")
        print('Example: uv run python scripts/batch_review.py "anthropic/claude-sonnet-4-6" "sonnet46"')
        sys.exit(1)

    model = sys.argv[1]
    model_label = sys.argv[2]
    paper_names = sys.argv[3:] if len(sys.argv) > 3 else list(PAPERS.keys())

    print(f"Model: {model} (label: {model_label})")
    print(f"Judge: {JUDGE_MODEL}")
    print(f"Papers: {', '.join(paper_names)}")
    print(f"Timestamp: {TODAY}")
    print(f"References: refine, stanford, reviewer3")

    all_results = []

    for paper_name in paper_names:
        if paper_name not in PAPERS:
            print(f"Unknown paper: {paper_name}, skipping")
            continue

        review_path, review_md, paper_text = run_review(paper_name, model, model_label)
        quality_results = run_quality_evals(paper_name, review_md, model_label, paper_text)

        all_results.append({
            "paper": paper_name,
            "review": review_path,
            "quality": quality_results,
        })

    # Summary
    print(f"\n{'='*90}")
    print(f"SUMMARY: {model_label} ({model}) — judged by {JUDGE_MODEL}")
    print(f"Timestamp: {TODAY}")
    print(f"{'='*90}")
    print(f"{'Paper':<25} {'Ref':<12} {'Overall':>8} {'Cov':>6} {'Spec':>6} {'Depth':>6} {'Fmt':>6}")
    print("-" * 90)
    for r in all_results:
        for q in r["quality"]:
            d = q["dimensions"]
            print(
                f"{r['paper']:<25} {q['ref']:<12} {q['overall']:>7.2f} "
                f"{d.get('coverage', 0):>5.1f} {d.get('specificity', 0):>5.1f} "
                f"{d.get('depth', 0):>5.1f} {d.get('format', 0):>5.1f}"
            )


if __name__ == "__main__":
    main()
