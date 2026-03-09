"""Quality-eval existing reviews that don't have quality scores yet."""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coarse.extraction import extract_text
from coarse.llm import LLMClient
from coarse.quality import evaluate_review, save_quality_report

BASE = Path(__file__).parent.parent / "data" / "refine_examples"
JUDGE_MODEL = "gemini/gemini-3.1-pro-preview"
TODAY = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# Existing sonnet reviews to evaluate
REVIEWS = [
    ("cortical_circuits", "review_sonnet46_20260306.md", "sonnet46"),
    ("coset_codes", "review_sonnet46_20260306.md", "sonnet46"),
    ("population_genetics", "review_sonnet46_20260306.md", "sonnet46"),
]

for paper_name, review_file, model_label in REVIEWS:
    paper_dir = BASE / paper_name
    review_path = paper_dir / review_file
    ref_path = paper_dir / "reference_review_stanford.md"
    pdf_path = paper_dir / "paper.pdf"

    if not review_path.exists():
        print(f"Skipping {paper_name}: {review_file} not found")
        continue

    print(f"\nEvaluating {paper_name}/{review_file}...")
    review_text = review_path.read_text(encoding="utf-8")
    ref_text = ref_path.read_text(encoding="utf-8")

    pt = extract_text(pdf_path)
    client = LLMClient(model=JUDGE_MODEL)
    report = evaluate_review(
        review_text, ref_text, client=client,
        paper_text=pt.full_markdown, model=JUDGE_MODEL,
    )

    quality_path = paper_dir / f"paper_quality_{model_label}_{TODAY}.md"
    save_quality_report(report, quality_path, str(ref_path), model=JUDGE_MODEL)

    print(f"  Overall: {report.overall_score:.2f}/6.0")
    for d in report.dimensions:
        print(f"    {d.dimension}: {d.score}")
    print(f"  Saved: {quality_path.name}")
