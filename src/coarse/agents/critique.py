"""Critique agent — self-critique quality gate that evaluates and revises DetailedComments."""
from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import CRITIQUE_SYSTEM, critique_system, critique_user
from coarse.types import DetailedComment, OverviewFeedback


class _RevisedComments(BaseModel):
    """Instructor response envelope for the revised, renumbered comment list."""

    comments: list[DetailedComment]


class CritiqueAgent(ReviewAgent):
    """Self-critique quality gate that evaluates each DetailedComment for specificity,
    accuracy, and actionability, revising weak ones and dropping low-value ones."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
        comment_target: int | str | None = None,
    ) -> list[DetailedComment]:
        user_content = critique_user(overview, comments)
        sys_prompt = critique_system(comment_target) if comment_target else CRITIQUE_SYSTEM

        messages = self._build_messages(sys_prompt, user_content)
        result = self.client.complete(
            messages, _RevisedComments, max_tokens=16384, temperature=0.1
        )
        return result.comments
