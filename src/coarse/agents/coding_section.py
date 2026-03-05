"""Coding section agent — uses OpenHands SDK for deep section analysis.

Routes proof, methodology, and results sections to a coding agent that can
cross-reference other sections, verify math with Python, and read the full paper.

run() signature matches SectionAgent.run() for drop-in pipeline swap.
"""
from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Type

from pydantic import BaseModel, Field

from coarse.agents.base import CodingReviewAgent
from coarse.agents.section import SectionAgent, _SectionComments
from coarse.coding_agent import DEFAULT_AGENT_TOOLS, run_agent_sync
from coarse.config import CoarseConfig
from coarse.llm import LLMClient
from coarse.prompts import SECTION_SYSTEM_MAP, SECTION_SYSTEM
from coarse.types import (
    DetailedComment,
    DomainCalibration,
    OverviewFeedback,
    SectionInfo,
)

logger = logging.getLogger(__name__)

# Self-contained script dropped into agent workspaces for quote verification.
# Uses the same fuzzy matching logic as coarse/quote_verify.py but with no
# package imports so it runs standalone in the temp workspace.
_VERIFY_QUOTE_SCRIPT = '''\
#!/usr/bin/env python3
"""Verify a quote against paper.md using fuzzy matching.

Usage: python verify_quote.py "your quote here"
"""
import difflib
import sys

MIN_MATCH_RATIO = 0.70

def find_nearest(quote, paper_text, window_factor=1.5):
    quote_len = len(quote)
    window_size = max(int(quote_len * window_factor), 50)
    step = max(1, quote_len // 4)
    best_ratio, best_passage = 0.0, ""
    ql = quote.lower()
    for i in range(0, len(paper_text) - min(quote_len, len(paper_text)) + 1, step):
        candidate = paper_text[i:i + window_size]
        ratio = difflib.SequenceMatcher(None, ql, candidate.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_passage = candidate
    if best_passage and best_ratio >= MIN_MATCH_RATIO:
        # Trim to best-matching substring
        best_sub, best_sub_ratio = best_passage[:quote_len], 0.0
        for start in range(0, len(best_passage) - quote_len + 1, max(1, quote_len // 8)):
            sub = best_passage[start:start + quote_len]
            r = difflib.SequenceMatcher(None, ql, sub.lower()).ratio()
            if r > best_sub_ratio:
                best_sub_ratio = r
                best_sub = sub
        best_passage = best_sub
    return best_passage, best_ratio

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_quote.py \\"your quote here\\"")
        sys.exit(1)
    quote = sys.argv[1]
    paper = open("paper.md", encoding="utf-8").read()
    # Exact match first
    if quote.lower() in paper.lower():
        print(f"EXACT MATCH found.")
        # Show location
        idx = paper.lower().index(quote.lower())
        line_num = paper[:idx].count("\\n") + 1
        print(f"Location: line {line_num}")
        sys.exit(0)
    passage, ratio = find_nearest(quote, paper)
    if ratio >= MIN_MATCH_RATIO:
        print(f"FUZZY MATCH (ratio={ratio:.2f})")
        print(f"Nearest passage: {passage!r}")
    else:
        print(f"NO MATCH (best ratio={ratio:.2f})")
        print("The quote does not appear in the paper. Use an exact verbatim quote.")
        sys.exit(1)
'''


def _build_section_index(all_sections: list[SectionInfo]) -> dict:
    """Build a keyword → section number index from claims and definitions."""
    index: dict[str, list] = {}
    for s in all_sections:
        section_ref = f"Section {s.number}: {s.title}"
        for claim in s.claims:
            index.setdefault(claim, []).append(section_ref)
        for defn in s.definitions:
            index.setdefault(defn, []).append(section_ref)
    return index


_TASK_TEMPLATE = """\
You are reviewing section "{section_title}" of the paper "{paper_title}".

Your workspace contains:
- `paper.md` — the full paper text (QA-corrected)
- `section.md` — the section you are reviewing (with metadata header)
- `other_sections/` — each other section as a numbered file
- `context.json` — overview issues, calibration, literature context
- `section_index.json` — keyword → section number mapping for cross-references
- `verify_quote.py` — quote verification script (see below)
- `example_output.json` — example of valid output format

Instructions:
1. Read `section.md` first to understand the section content.
2. Use grep to cross-reference claims, definitions, and equations:
   - `grep -n "search term" paper.md` — shows line numbers for precise location
   - `grep -i -C 3 "search term" paper.md` — case-insensitive with 3 lines of context
   - `grep -n "definition" other_sections/*.md` — search across all sections
   - Check `section_index.json` first to find which section defines a term.
3. If the section contains equations, verify them using Python (stdlib math only —
   do NOT assume numpy or sympy are installed).
4. For each issue found, include an EXACT verbatim quote from section.md.
   Do NOT modify, paraphrase, or reconstruct quotes.
   Verify each quote: `python verify_quote.py "your quote here"`
5. Write your output to `_review_output.json` following the schema in
   `example_output.json`.

Produce 1-5 comments. Focus on concrete errors you can demonstrate.
"""


class CodingSectionAgent(CodingReviewAgent):
    """Deep section reviewer using OpenHands SDK.

    Falls back to standard SectionAgent on any failure.
    """

    def output_schema(self) -> Type[BaseModel]:
        return _SectionComments

    def prepare_workspace(
        self,
        workspace: Path,
        section: SectionInfo,
        paper_markdown: str,
        all_sections: list[SectionInfo],
        paper_title: str,
        overview: OverviewFeedback | None = None,
        calibration: DomainCalibration | None = None,
        focus: str = "general",
        literature_context: str = "",
    ) -> str:
        """Write context files to workspace. Return the task prompt."""
        # Full paper
        (workspace / "paper.md").write_text(paper_markdown, encoding="utf-8")

        # Section being reviewed (with metadata header)
        header_parts = [
            f"# Section {section.number}: {section.title}",
            f"Type: {section.section_type.value}",
        ]
        if section.claims:
            header_parts.append("Claims: " + "; ".join(section.claims))
        if section.definitions:
            header_parts.append("Definitions: " + "; ".join(section.definitions))
        section_content = "\n".join(header_parts) + "\n\n" + section.text
        (workspace / "section.md").write_text(section_content, encoding="utf-8")

        # Other sections as numbered files
        other_dir = workspace / "other_sections"
        other_dir.mkdir(exist_ok=True)
        for s in all_sections:
            if s.number == section.number and s.title == section.title:
                continue
            filename = f"{s.number:02}_{s.title.lower().replace(' ', '_')[:40]}.md" if isinstance(s.number, int) else f"{s.number}_{s.title.lower().replace(' ', '_')[:40]}.md"
            (other_dir / filename).write_text(
                f"# Section {s.number}: {s.title}\n\n{s.text}", encoding="utf-8"
            )

        # Context JSON
        context: dict = {"paper_title": paper_title}
        if overview and overview.issues:
            context["overview_issues"] = [
                {"title": issue.title, "body": issue.body}
                for issue in overview.issues
            ]
        if calibration:
            context["calibration"] = calibration.model_dump()
        if literature_context:
            context["literature_context"] = literature_context
        if section.claims:
            context["section_claims"] = section.claims
        if section.definitions:
            context["section_definitions"] = section.definitions
        (workspace / "context.json").write_text(
            json.dumps(context, indent=2), encoding="utf-8"
        )

        # Quote verification script
        (workspace / "verify_quote.py").write_text(_VERIFY_QUOTE_SCRIPT, encoding="utf-8")

        # Section cross-reference index
        section_index = _build_section_index(all_sections)
        (workspace / "section_index.json").write_text(
            json.dumps(section_index, indent=2), encoding="utf-8"
        )

        # Example output (concrete example helps agents produce valid JSON)
        example = {
            "comments": [
                {
                    "number": 1,
                    "title": "Sign error in change-of-variables",
                    "quote": "Applying the substitution u = 1 - t, we obtain the integral equals 2pi.",
                    "feedback": (
                        "The substitution u = 1 - t gives du = -dt, so the limits reverse. "
                        "The correct result is -2pi, not 2pi. This affects Theorem 3.2 downstream."
                    ),
                    "severity": "critical",
                }
            ]
        }
        (workspace / "example_output.json").write_text(
            json.dumps(example, indent=2), encoding="utf-8"
        )

        return _TASK_TEMPLATE.format(
            section_title=section.title, paper_title=paper_title,
        )

    def run(
        self,
        section: SectionInfo,
        paper_title: str,
        overview: OverviewFeedback | None = None,
        calibration: DomainCalibration | None = None,
        focus: str = "general",
        literature_context: str = "",
        *,
        paper_markdown: str = "",
        all_sections: list[SectionInfo] | None = None,
    ) -> list[DetailedComment]:
        """Review a section using a coding agent. Falls back to SectionAgent on failure.

        Extra kwargs paper_markdown and all_sections are required for the coding agent
        but not part of the standard SectionAgent signature. The pipeline provides them.
        """
        system_prompt = SECTION_SYSTEM_MAP.get(focus, SECTION_SYSTEM)

        # Proof/methodology sections need more turns for derivation checking
        turns = 25 if focus == "proof" else 15

        try:
            with tempfile.TemporaryDirectory(prefix="coarse_section_") as tmpdir:
                workspace = Path(tmpdir)
                task_prompt = self.prepare_workspace(
                    workspace,
                    section=section,
                    paper_markdown=paper_markdown,
                    all_sections=all_sections or [],
                    paper_title=paper_title,
                    overview=overview,
                    calibration=calibration,
                    focus=focus,
                    literature_context=literature_context,
                )
                result = run_agent_sync(
                    task_prompt=task_prompt,
                    system_prompt=system_prompt,
                    output_schema=_SectionComments,
                    working_directory=workspace,
                    allowed_tools=DEFAULT_AGENT_TOOLS,
                    max_turns=turns,
                    model=self.config.agent_model,
                    max_budget_usd=0.50,
                    timeout=120.0,
                    config=self.config,
                )
                return result.comments
        except Exception:
            logger.warning(
                "Coding agent failed for section '%s', falling back to standard agent",
                section.title,
                exc_info=True,
            )
            if self.fallback_client is None:
                raise
            fallback = SectionAgent(self.fallback_client)
            return fallback.run(
                section, paper_title, overview, calibration, focus, literature_context,
            )
