"""Crossref agent — deduplicates, quote-verifies, and renumbers DetailedComments."""
from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import CROSSREF_SYSTEM, crossref_user
from coarse.types import DetailedComment, OverviewFeedback, PaperText


class _ConsolidatedComments(BaseModel):
    """Instructor response envelope for the consolidated, renumbered comment list."""

    comments: list[DetailedComment]


class CrossrefAgent(ReviewAgent):
    """Deduplicates near-identical comments, verifies quotes against paper text,
    and returns a globally renumbered list of DetailedComment."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    # Max chars of paper text to send for quote verification
    MAX_PAPER_CHARS = 80_000

    def run(  # type: ignore[override]
        self,
        paper_text: PaperText,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
    ) -> list[DetailedComment]:
        # Truncate very long papers to keep within context window
        text = paper_text.full_markdown
        if len(text) > self.MAX_PAPER_CHARS:
            text = text[: self.MAX_PAPER_CHARS] + "\n\n[...truncated]"
        user_content = crossref_user(text, overview, comments)
        messages = [
            {"role": "system", "content": CROSSREF_SYSTEM},
            {"role": "user", "content": user_content},
        ]
        result = self.client.complete(
            messages, _ConsolidatedComments, max_tokens=32768, temperature=0.1
        )
        return result.comments
