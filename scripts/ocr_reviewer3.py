"""One-time script to OCR reviewer3 PDFs into markdown text files.

Usage:
    uv run python scripts/ocr_reviewer3.py

Requires OPENROUTER_API_KEY in environment or .env file — extraction
routes through OpenRouter's Mistral OCR file-parser plugin.
"""
from pathlib import Path

from coarse.extraction import extract_text

DATA_ROOT = Path(__file__).resolve().parent.parent / "data" / "refine_examples"

PDFS = [
    DATA_ROOT / "coset_codes" / "review_reviewer3.pdf",
    DATA_ROOT / "population_genetics" / "review_reviewer3.pdf",
    DATA_ROOT / "cortical_circuits" / "review_reviewer3.pdf",
]


def main() -> None:
    for pdf in PDFS:
        if not pdf.exists():
            print(f"SKIP {pdf} (not found)")
            continue

        out = pdf.with_suffix(".md")
        if out.exists():
            print(f"SKIP {pdf.name} (already extracted to {out.name})")
            continue

        print(f"OCR  {pdf} ...")
        paper_text = extract_text(pdf, use_cache=False)
        out.write_text(paper_text.full_markdown, encoding="utf-8")
        print(f"  → {out.name} ({len(paper_text.full_markdown)} chars)")

    print("Done.")


if __name__ == "__main__":
    main()
