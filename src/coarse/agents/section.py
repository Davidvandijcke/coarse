"""Section agent — produces DetailedComments for a single paper section."""
from __future__ import annotations

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent, truncate_section
from coarse.prompts import (
    SECTION_SYSTEM,
    SECTION_SYSTEM_MAP,
    section_user,
)
from coarse.types import DetailedComment, DomainCalibration, OverviewFeedback, SectionInfo

_TEMPERATURE = 0.3


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

    def run(  # type: ignore[override]
        self,
        section: SectionInfo,
        paper_title: str,
        overview: "OverviewFeedback | None" = None,
        calibration: "DomainCalibration | None" = None,
        focus: str = "general",
        literature_context: str = "",
        all_sections: "list[SectionInfo] | None" = None,
        abstract: str = "",
    ) -> list[DetailedComment]:
        truncated = truncate_section(section)

        system_prompt = SECTION_SYSTEM_MAP.get(focus, SECTION_SYSTEM)
        user_text = section_user(
            paper_title, truncated, overview=overview, calibration=calibration,
            literature_context=literature_context,
            all_sections=all_sections,
            abstract=abstract,
        )

        messages = self._build_messages(system_prompt, user_text)

        result = self.client.complete(
            messages, _SectionComments, max_tokens=16384, temperature=_TEMPERATURE
        )
        return result.comments
