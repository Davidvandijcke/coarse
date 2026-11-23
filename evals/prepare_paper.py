"""Prepare a benchmark paper: extract, analyze structure, atomize its reference.

Held-out papers for the arm comparison. Their reference reviews are in the
same format as the benchmark's, so the reference is atomized mechanically here
rather than by hand: one finding per macro issue and one per detailed comment,
with no further splitting. That is coarser than the hand-atomized benchmark
reference, but it is applied identically to every held-out paper, so arms are
compared on the same basis.

Usage:
    OPENROUTER_API_KEY=... uv run python evals/prepare_paper.py \
        --id coset_codes \
        --pdf data/refine_examples/coset_codes/paper.pdf \
        --reference data/refine_examples/feedback-coset-codes-...md
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
from pathlib import Path

from coarse.config import load_config
from coarse.extraction import extract_file
from coarse.llm import LLMClient
from coarse.structure import analyze_structure

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("prepare_paper")

# "**Issue Title**" lines inside Overall Feedback.
_ISSUE_RE = re.compile(r"^\*\*(.+?)\*\*\s*$", re.MULTILINE)
# "### N. Title" detailed-comment headers.
_COMMENT_RE = re.compile(r"^###\s*(\d+)\.\s*(.+?)$", re.MULTILINE)
_QUOTE_RE = re.compile(r"\*\*Quote\*\*:\s*\n((?:>.*\n?|\n(?=>))*)", re.MULTILINE)
_FEEDBACK_RE = re.compile(r"\*\*Feedback\*\*:\s*\n(.+?)(?=\n---|\n###|\Z)", re.DOTALL)
_IMPORTANCE_RE = re.compile(r"\*\*Importance\*\*:\s*(\w+)", re.IGNORECASE)

_SKIP_ISSUE_TITLES = {"status", "recommendation", "key revision targets"}


def atomize_reference(markdown: str) -> list[dict]:
    """One finding per macro issue and per detailed comment."""
    findings: list[dict] = []

    overall_start = markdown.find("## Overall Feedback")
    detailed_start = markdown.find("## Detailed Comments")
    overall = markdown[overall_start : detailed_start if detailed_start > 0 else len(markdown)]

    for i, match in enumerate(_ISSUE_RE.finditer(overall), start=1):
        title = match.group(1).strip()
        if title.lower().rstrip(":") in _SKIP_ISSUE_TITLES:
            continue
        body_start = match.end()
        next_match = _ISSUE_RE.search(overall, body_start)
        body = overall[body_start : next_match.start() if next_match else len(overall)]
        body = body.strip()
        if len(body) < 80:
            continue
        findings.append(
            {
                "id": f"O{i}",
                "origin": "overall",
                "importance": "major",
                "location": "",
                "claim": f"{title}. {body}"[:4000],
                "tags": [],
            }
        )

    if detailed_start > 0:
        detailed = markdown[detailed_start:]
        headers = list(_COMMENT_RE.finditer(detailed))
        for i, match in enumerate(headers):
            block_end = headers[i + 1].start() if i + 1 < len(headers) else len(detailed)
            block = detailed[match.end() : block_end]
            feedback = _FEEDBACK_RE.search(block)
            quote = _QUOTE_RE.search(block)
            importance = _IMPORTANCE_RE.search(block)
            claim = (feedback.group(1).strip() if feedback else block.strip())[:4000]
            if len(claim) < 40:
                continue
            findings.append(
                {
                    "id": f"D{match.group(1)}",
                    "origin": "detailed",
                    "importance": (importance.group(1).lower() if importance else "major"),
                    "location": (quote.group(1).strip().lstrip("> ")[:160] if quote else ""),
                    "claim": claim,
                    "tags": [],
                }
            )
    return findings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--reference", required=True, type=Path)
    ap.add_argument("--model", default="openrouter/anthropic/claude-opus-5.5")
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    out_dir = Path("evals/papers") / args.id
    out_dir.mkdir(parents=True, exist_ok=True)
    local_pdf = out_dir / "paper.pdf"
    if not local_pdf.exists():
        shutil.copy(args.pdf, local_pdf)
    # Carry the extraction cache across so extraction is not re-paid.
    for cache in args.pdf.parent.glob("*.extraction_cache.json"):
        target = out_dir / "paper.extraction_cache.json"
        if not target.exists():
            shutil.copy(cache, target)

    paper_text = extract_file(local_pdf)
    (out_dir / "paper.md").write_text(paper_text.full_markdown, encoding="utf-8")
    logger.info(
        "extracted %d chars (garble %.4f)",
        len(paper_text.full_markdown),
        paper_text.garble_ratio,
    )

    client = LLMClient(model=args.model, config=load_config())
    structure = analyze_structure(paper_text, client)
    (out_dir / "structure.json").write_text(
        json.dumps(structure.model_dump(mode="json"), indent=1), encoding="utf-8"
    )
    logger.info("structure: %d sections, title %r", len(structure.sections), structure.title)

    reference_md = args.reference.read_text(encoding="utf-8")
    (out_dir / "reference.md").write_text(reference_md, encoding="utf-8")
    findings = atomize_reference(reference_md)
    reference = {
        "paper_id": args.id,
        "title": args.title or structure.title,
        "source_pdf": str(local_pdf),
        "reference": {
            "file": str(out_dir / "reference.md"),
            "kind": "full_reference_review",
            "note": (
                "Atomized mechanically: one finding per macro issue and per detailed "
                "comment, no further splitting. Precision is adjudicated against the "
                "paper, never against this file."
            ),
        },
        "findings": findings,
    }
    ref_path = Path("evals/references") / f"{args.id}.json"
    ref_path.write_text(json.dumps(reference, indent=1), encoding="utf-8")
    logger.info("atomized %d reference findings -> %s", len(findings), ref_path)
    print(f"structure sections: {len(structure.sections)}")
    print(f"reference findings: {len(findings)}")
    for f in findings:
        print(f"  {f['id']:5} {f['origin']:9} {f['importance']:9} {f['claim'][:90]}")


if __name__ == "__main__":
    main()
