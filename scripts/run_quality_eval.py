"""Run quality evaluation: 3 models × 2 references × 4 papers = 24 evals.

Usage:
    uv run python scripts/run_quality_eval.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from coarse.llm import LLMClient
from coarse.quality import evaluate_review, save_quality_report

BASE = Path(__file__).resolve().parent.parent / "data" / "refine_examples"
EVAL_MODEL = "openrouter/google/gemini-3.1-pro-preview"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PAPERS = {
    "cortical_circuits": {
        "reviews": {
            "qwen35plus": "review_qwen35plus_20260308_130637.md",
            "sonnet46": "review_sonnet46_20260308_131015.md",
            "kimik25": "review_kimik25_20260308_135543.md",
        },
        "reviewer3": "review_reviewer3.md",
    },
    "coset_codes": {
        "reviews": {
            "qwen35plus": "review_qwen35plus_20260308_130637.md",
            "sonnet46": "review_sonnet46_20260308_131015.md",
            "kimik25": "review_kimik25_20260308_153416.md",
        },
        "reviewer3": "review_reviewer3.md",
    },
    "population_genetics": {
        "reviews": {
            "qwen35plus": "review_qwen35plus_20260308_134638.md",
            "sonnet46": "review_sonnet46_20260308_131015.md",
            "kimik25": "review_kimik25_20260308_223614.md",
        },
        "reviewer3": "review_reviewer3.md",
    },
    "targeting_interventions": {
        "reviews": {
            "qwen35plus": "review_qwen35plus_20260308_134638.md",
            "sonnet46": "review_sonnet46_20260308_130643.md",
            "kimik25": "review_kimik25_20260308_233034.md",
        },
        "reviewer3": "reviewer3_review.md",
    },
}


def main() -> None:
    client = LLMClient(model=EVAL_MODEL)
    total = 0
    failed = 0

    for paper_name, info in PAPERS.items():
        paper_dir = BASE / paper_name
        print(f"\n{'='*60}")
        print(f"Paper: {paper_name}")
        print(f"{'='*60}")

        # Load paper text from extraction cache
        cache_path = paper_dir / "paper.extraction_cache.json"
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        paper_text = cache["full_markdown"]

        # Load references
        stanford_ref = (paper_dir / "reference_review_stanford.md").read_text(encoding="utf-8")
        reviewer3_ref = (paper_dir / info["reviewer3"]).read_text(encoding="utf-8")

        references = [
            ("stanford", stanford_ref),
            ("reviewer3", reviewer3_ref),
        ]

        for model_name, review_file in info["reviews"].items():
            generated = (paper_dir / review_file).read_text(encoding="utf-8")

            for ref_name, ref_text in references:
                total += 1
                out_path = paper_dir / f"quality_{model_name}_vs_{ref_name}_{TIMESTAMP}.md"
                print(f"  [{total}/24] {model_name} vs {ref_name}...", end=" ", flush=True)

                try:
                    report = evaluate_review(
                        generated,
                        ref_text,
                        client=client,
                        paper_text=paper_text,
                        model=EVAL_MODEL,
                    )
                    save_quality_report(
                        report, out_path, ref_name, model=EVAL_MODEL, mode="single"
                    )
                    print(f"{report.overall_score:.2f}/6 -> {out_path.name}")
                except Exception as e:
                    failed += 1
                    print(f"FAILED: {e}")

    print(f"\nDone: {total - failed}/{total} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
