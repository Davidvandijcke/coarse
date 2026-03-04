"""Coding critique agent — uses OpenHands SDK to verify comments against paper text.

The critique agent can grep the paper for quoted text, verify claims are accurate,
and check math equations. Falls back to standard CritiqueAgent on failure.

run() signature matches CritiqueAgent.run() for drop-in pipeline swap.
"""
from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from typing import Type

from pydantic import BaseModel

from coarse.agents.base import CodingReviewAgent
from coarse.agents.critique import CritiqueAgent, _RevisedComments
from coarse.coding_agent import DEFAULT_AGENT_TOOLS, run_agent_sync
from coarse.config import CoarseConfig
from coarse.llm import LLMClient
from coarse.prompts import CRITIQUE_SYSTEM, critique_system
from coarse.types import DetailedComment, OverviewFeedback, SectionInfo

logger = logging.getLogger(__name__)


_TASK_TEMPLATE = """\
You are performing a final quality evaluation of review comments for a research paper.

Your workspace contains:
- `paper.md` — the full paper text
- `overview.json` — the overview feedback (macro-level issues)
- `comments.json` — the comments to evaluate
- `sections/` — individual section files with headings
- `example_output.json` — example of valid output format

Instructions:
1. For EACH comment in `comments.json`:
   a. Grep `paper.md` for the quoted text — verify it exists verbatim.
   b. Read surrounding context to verify the claim is accurate.
   c. If the comment claims a math error, check the equations using Python
      (stdlib math only — do NOT assume numpy or sympy are installed).
2. Do NOT modify the `quote` field unless you find the exact verbatim passage
   and the current quote is a paraphrase. In that case, replace with the real text.
3. Remove comments that are:
   - Based on quotes not found in the paper
   - Making inaccurate claims about the paper's content
   - Generic advice that could apply to any paper
   - Requesting additional analyses rather than identifying errors
4. Assign severity: critical / major / minor
5. Target approximately {comment_target} comments total.
6. Write your output to `_review_output.json`.
"""


class CodingCritiqueAgent(CodingReviewAgent):
    """Deep critique agent using OpenHands SDK.

    Verifies each comment's quote and claims against the actual paper text.
    Falls back to standard CritiqueAgent on any failure.
    """

    def output_schema(self) -> Type[BaseModel]:
        return _RevisedComments

    def prepare_workspace(
        self,
        workspace: Path,
        paper_markdown: str,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
        all_sections: list[SectionInfo] | None = None,
    ) -> str:
        """Write context files to workspace. Return the task prompt."""
        # Full paper
        (workspace / "paper.md").write_text(paper_markdown, encoding="utf-8")

        # Overview
        (workspace / "overview.json").write_text(
            overview.model_dump_json(indent=2), encoding="utf-8"
        )

        # Comments to evaluate
        comments_data = [c.model_dump() for c in comments]
        (workspace / "comments.json").write_text(
            json.dumps(comments_data, indent=2), encoding="utf-8"
        )

        # Individual sections
        if all_sections:
            sections_dir = workspace / "sections"
            sections_dir.mkdir(exist_ok=True)
            for s in all_sections:
                filename = f"{s.number:02}_{s.title.lower().replace(' ', '_')[:40]}.md" if isinstance(s.number, int) else f"{s.number}_{s.title.lower().replace(' ', '_')[:40]}.md"
                (sections_dir / filename).write_text(
                    f"# Section {s.number}: {s.title}\n\n{s.text}", encoding="utf-8"
                )

        # Example output
        example = {
            "comments": [
                {
                    "number": 1,
                    "title": "Sign error in Theorem 3.2",
                    "quote": "The integral evaluates to 2pi by the substitution u = 1 - t.",
                    "feedback": (
                        "Verified: this quote appears on page 7. The substitution u = 1-t "
                        "gives du = -dt, reversing limits. Correct result is -2pi."
                    ),
                    "severity": "critical",
                }
            ]
        }
        (workspace / "example_output.json").write_text(
            json.dumps(example, indent=2), encoding="utf-8"
        )

        # Compute target
        comment_target = max(6, len(comments) // 2)
        return _TASK_TEMPLATE.format(comment_target=comment_target)

    def run(
        self,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
        comment_target: int | str | None = None,
        *,
        paper_markdown: str = "",
        all_sections: list[SectionInfo] | None = None,
    ) -> list[DetailedComment]:
        """Evaluate comments using a coding agent. Falls back to CritiqueAgent on failure.

        Extra kwargs paper_markdown and all_sections are required for the coding agent
        but not part of the standard CritiqueAgent signature. The pipeline provides them.
        """
        try:
            with tempfile.TemporaryDirectory(prefix="coarse_critique_") as tmpdir:
                workspace = Path(tmpdir)
                task_prompt = self.prepare_workspace(
                    workspace,
                    paper_markdown=paper_markdown,
                    overview=overview,
                    comments=comments,
                    all_sections=all_sections,
                )
                result = run_agent_sync(
                    task_prompt=task_prompt,
                    system_prompt=critique_system(comment_target) if comment_target else CRITIQUE_SYSTEM,
                    output_schema=_RevisedComments,
                    working_directory=workspace,
                    allowed_tools=DEFAULT_AGENT_TOOLS,
                    max_turns=20,
                    model=self.config.agent_model,
                    max_budget_usd=1.00,
                    timeout=180.0,
                    config=self.config,
                )
                return result.comments
        except Exception:
            logger.warning(
                "Coding critique agent failed, falling back to standard agent",
                exc_info=True,
            )
            if self.fallback_client is None:
                raise
            fallback = CritiqueAgent(self.fallback_client)
            return fallback.run(overview, comments, comment_target)
