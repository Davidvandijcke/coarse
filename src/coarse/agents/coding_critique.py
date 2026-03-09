"""Coding critique agent — uses OpenAI Agents SDK to verify comments against paper text.

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

from coarse.agents.base import CodingReviewAgent, section_filename
from coarse.agents.coding_section import _VERIFY_QUOTE_SCRIPT
from coarse.agents.critique import CritiqueAgent, _RevisedComments
from coarse.coding_agent import run_agent_sync
from coarse.prompts import CRITIQUE_SYSTEM, critique_system
from coarse.types import DetailedComment, OverviewFeedback, SectionInfo

logger = logging.getLogger(__name__)

# Agent resource limits
_MAX_TURNS = 30
_MAX_BUDGET_USD = 5.00
_TIMEOUT = 600.0


_TASK_TEMPLATE = """\
Evaluate review comments for a research paper. Target ~{comment_target} comments.

Workspace: `paper.md` (full paper), `comments.json` (comments to evaluate), \
`overview.json` (overview).

Steps:
1. Read `comments.json`.
2. For each comment, verify the quote exists: `run_command('grep -i -c "key phrase" paper.md')`.
3. Remove comments with fabricated quotes, inaccurate claims, or generic advice.
4. For each surviving comment, call `add_comment(number, title, quote, feedback, severity)` \
with the corrected quote and severity (critical/major/minor).

IMPORTANT: Call `add_comment()` for each surviving comment. Do NOT write JSON files manually.
"""


class CodingCritiqueAgent(CodingReviewAgent):
    """Deep critique agent using OpenAI Agents SDK.

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
                (sections_dir / section_filename(s)).write_text(
                    f"# Section {s.number}: {s.title}\n\n{s.text}", encoding="utf-8"
                )

        # Quote verification script
        (workspace / "verify_quote.py").write_text(_VERIFY_QUOTE_SCRIPT, encoding="utf-8")

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
                    max_turns=_MAX_TURNS,
                    model=self.config.agent_model,
                    max_budget_usd=_MAX_BUDGET_USD,
                    timeout=_TIMEOUT,
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
