"""Live driver for the cross-language review-consistency eval (PR-F).

Runs the full review pipeline on a paper once in English (baseline) and once per
requested language, then compares them with ``coarse.lang_eval`` to decide
whether the shipped direct-in-language design (A) is sufficient or whether the
English-pivot design (B / PR-G) would help for any language.

WARNING: this makes PAID LLM calls — one full review per language PLUS the
English baseline (so `--languages Spanish,Arabic` = 3 reviews per paper). Run it
manually with API keys configured; it is not part of CI or the request path.

Usage:
    uv run python scripts/lang_eval_run.py paper.pdf --languages "Spanish,Arabic"
    uv run python scripts/lang_eval_run.py paper.pdf --languages French --model <model-id>

Decision criteria (see coarse.lang_eval.recommend): a language passes ("design A
sufficient") only if issue overlap with the English baseline clears the
consistency threshold AND quote fidelity stays high and doesn't trail English.
Languages that fail are the evidence for building the English-pivot design.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coarse.lang_eval import compare_languages, format_report  # noqa: E402
from coarse.pipeline import review_paper  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lang_eval_run")
    parser.add_argument("paper", type=Path, help="Path to the paper to review")
    parser.add_argument(
        "--languages",
        required=True,
        help="Comma-separated language names to evaluate, e.g. 'Spanish,Arabic'",
    )
    parser.add_argument("--model", default=None, help="Optional model override")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the report (also printed to stdout)",
    )
    args = parser.parse_args(argv)

    languages = [name.strip() for name in args.languages.split(",") if name.strip()]
    if not languages:
        print("ERROR: --languages must list at least one language", file=sys.stderr)
        return 2

    paper = str(args.paper)
    print(f"[lang_eval] English baseline review of {paper} ...", file=sys.stderr)
    english_review, _md, paper_text = review_paper(paper, model=args.model, skip_cost_gate=True)

    localized = {}
    for language in languages:
        print(f"[lang_eval] {language} review ...", file=sys.stderr)
        review, _m, _pt = review_paper(
            paper, model=args.model, skip_cost_gate=True, language=language
        )
        localized[language] = review

    report = compare_languages(
        english_review, localized, paper_text.full_markdown, paper=paper
    )
    text = format_report(report)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"\n[lang_eval] wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
