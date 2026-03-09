"""Crossref agent — deduplicates and renumbers DetailedComments.

Quote verification is handled by the programmatic verify_quotes() step
that runs after crossref in the pipeline.
"""
from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import CROSSREF_SYSTEM, crossref_system, crossref_user
from coarse.types import DetailedComment, OverviewFeedback


class _ConsolidatedComments(BaseModel):
    """Instructor response envelope for the consolidated, renumbered comment list."""

    comments: list[DetailedComment]


class CrossrefAgent(ReviewAgent):
    """Deduplicates near-identical comments and returns a globally renumbered
    list of DetailedComment."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
        comment_target: int | str | None = None,
    ) -> list[DetailedComment]:
        user_content = crossref_user(overview, comments)
        sys_prompt = crossref_system(comment_target) if comment_target else CROSSREF_SYSTEM
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content},
        ]
        result = self.client.complete(
            messages, _ConsolidatedComments, max_tokens=32768, temperature=0.1
        )
        return result.comments
