"""Editorial agent — merged filtering pass with full paper context.

Replaces the previous crossref → contradiction → critique pipeline with a single
LLM call that has access to the full paper text, overview issues, contribution
context, and all draft comments. Performs deduplication, contradiction checking,
quality filtering, severity assignment, notation capping, humanization, and
importance ordering in one pass.
"""
from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import EDITORIAL_SYSTEM, editorial_system, editorial_user
from coarse.types import ContributionContext, DetailedComment, OverviewFeedback

_TEMPERATURE = 0.15


class _EditorialComments(BaseModel):
    """Instructor response envelope for the editorially filtered comment list."""

    comments: list[DetailedComment]


class EditorialAgent(ReviewAgent):
    """Single-pass editorial filter that replaces crossref + contradiction + critique.

    Receives the full paper text so it can verify quotes, check absence claims,
    and make informed filtering decisions.
    """

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        paper_text: str,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
        comment_target: int | str | None = None,
        title: str = "",
        abstract: str = "",
        contribution_context: ContributionContext | None = None,
    ) -> list[DetailedComment]:
        user_content = editorial_user(
            paper_text, overview, comments,
            title=title, abstract=abstract,
            contribution_context=contribution_context,
        )
        sys_prompt = editorial_system(comment_target) if comment_target else EDITORIAL_SYSTEM

        messages = self._build_messages(sys_prompt, user_content)
        result = self.client.complete(
            messages, _EditorialComments, max_tokens=32768, temperature=_TEMPERATURE
        )
        return result.comments
