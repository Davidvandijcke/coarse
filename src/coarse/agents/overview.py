"""Overview agent — produces macro-level OverviewFeedback from a PaperStructure."""
from __future__ import annotations

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import OVERVIEW_SYSTEM, overview_user
from coarse.types import OverviewFeedback, PaperStructure, SectionInfo


def _build_sections_summary(sections: list[SectionInfo]) -> str:
    """Convert sections list to a condensed text block for the overview prompt.

    Each section is formatted as:
        ## {number}. {title} ({section_type})
        Claims: {claims joined by semicolons}
    """
    parts = []
    for sec in sections:
        claims_str = "; ".join(sec.claims) if sec.claims else "(none)"
        parts.append(
            f"## {sec.number}. {sec.title} ({sec.section_type.value})\n"
            f"Claims: {claims_str}"
        )
    return "\n\n".join(parts)


class OverviewAgent(ReviewAgent):
    """Produces 4-6 macro-level issues from a PaperStructure."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(self, structure: PaperStructure) -> OverviewFeedback:  # type: ignore[override]
        sections_summary = _build_sections_summary(structure.sections)
        messages = [
            {"role": "system", "content": OVERVIEW_SYSTEM},
            {
                "role": "user",
                "content": overview_user(structure.title, structure.abstract, sections_summary),
            },
        ]
        return self.client.complete(  # type: ignore[return-value]
            messages, OverviewFeedback, max_tokens=2048, temperature=0.3
        )
