"""Section agent — produces DetailedComments for a single paper section."""
from __future__ import annotations

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import SECTION_SYSTEM, section_user
from coarse.types import DetailedComment, SectionInfo


class _SectionComments(BaseModel):
    """Instructor response envelope for section-level detailed comments.

    numbers are local per-section (1–N); downstream crossref agent
    renumbers comments globally across all sections.
    """

    comments: list[DetailedComment] = Field(min_length=1, max_length=5)


class SectionAgent(ReviewAgent):
    """Produces 1-5 DetailedComments for a single paper section.

    Contract: comment numbers are local (1-N within this section).
    The crossref agent is responsible for global renumbering.
    """

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    # Maximum section text length (chars) sent to the LLM.
    # Sections longer than this are truncated to avoid token limits.
    MAX_SECTION_CHARS = 15_000

    def run(self, section: SectionInfo, paper_title: str) -> list[DetailedComment]:  # type: ignore[override]
        # Truncate very long sections to avoid token overflow
        if len(section.text) > self.MAX_SECTION_CHARS:
            truncated = section.model_copy(
                update={"text": section.text[: self.MAX_SECTION_CHARS] + "\n\n[...truncated]"}
            )
        else:
            truncated = section

        messages = [
            {"role": "system", "content": SECTION_SYSTEM},
            {"role": "user", "content": section_user(paper_title, truncated)},
        ]
        result = self.client.complete(
            messages, _SectionComments, max_tokens=4096, temperature=0.3
        )
        return result.comments
