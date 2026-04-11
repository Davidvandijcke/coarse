"""Overview agent — produces macro-level OverviewFeedback from a PaperStructure."""

from __future__ import annotations

import logging

from coarse.agents.base import MAX_CONTEXT_CHARS, ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import (
    ASSUMPTION_CHECK_SYSTEM,
    OVERVIEW_SYSTEM,
    assumption_check_user,
    document_form_notice,
    overview_paper_context,
    overview_user,
)
from coarse.types import (
    DomainCalibration,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    SectionInfo,
    SectionType,
)

logger = logging.getLogger(__name__)

_OVERVIEW_TEMPERATURE = 0.5


def _build_sections_text(sections: list[SectionInfo]) -> str:
    """Convert sections list to a text block with full, untruncated text."""
    parts: list[str] = []
    for sec in sections:
        if not sec.text:
            parts.append(f"## {sec.number}. {sec.title} ({sec.section_type.value})\n(empty)")
            continue
        parts.append(f"## {sec.number}. {sec.title} ({sec.section_type.value})\n{sec.text}")
    return "\n\n".join(parts)


class OverviewAgent(ReviewAgent):
    """Produces macro-level issues from a PaperStructure."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        structure: PaperStructure,
        calibration: DomainCalibration | None = None,
        literature_context: str = "",
    ) -> OverviewFeedback:
        sections_text = _build_sections_text(structure.sections)

        # Append the document-form addendum to the system prompt. Empty string
        # for manuscripts/preprints so that path is unchanged; a tailored block
        # for outlines/drafts/proposals/etc. that relaxes the peer-review frame.
        system_prompt = OVERVIEW_SYSTEM + document_form_notice(structure.document_form)

        if self.client.supports_prompt_caching:
            paper_context = overview_paper_context(
                structure.title,
                structure.abstract,
                sections_text,
                calibration=calibration,
                literature_context=literature_context,
            )
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": paper_context,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {"type": "text", "text": system_prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": overview_user(
                        structure.title,
                        structure.abstract,
                        sections_text,
                        cache_mode=True,
                    ),
                },
            ]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": overview_user(
                        structure.title,
                        structure.abstract,
                        sections_text,
                        calibration=calibration,
                        literature_context=literature_context,
                    ),
                },
            ]

        return self.client.complete(  # type: ignore[return-value]
            messages, OverviewFeedback, max_tokens=8192, temperature=_OVERVIEW_TEMPERATURE
        )


# Section types relevant for assumption checking
_ASSUMPTION_RELEVANT_TYPES = {
    SectionType.INTRODUCTION,
    SectionType.METHODOLOGY,
    SectionType.RESULTS,
    SectionType.DISCUSSION,
    SectionType.OTHER,
}


def check_assumptions(
    structure: PaperStructure,
    client: LLMClient,
    calibration: DomainCalibration | None = None,
) -> list[OverviewIssue]:
    """Focused check: are theoretical assumptions consistent with empirical methods?

    Extracts assumption-relevant sections (intro, methodology, results,
    discussion, other), sends to LLM for consistency check.
    Returns 0-3 OverviewIssue objects.
    """
    relevant_sections = [
        s
        for s in structure.sections
        if s.section_type in _ASSUMPTION_RELEVANT_TYPES and len(s.text) > 50
    ]
    if not relevant_sections:
        return []

    # Build condensed text from relevant sections (cap at 500K chars)
    sections_text = "\n\n".join(f"## {s.number}. {s.title}\n{s.text}" for s in relevant_sections)
    if len(sections_text) > MAX_CONTEXT_CHARS:
        sections_text = sections_text[:MAX_CONTEXT_CHARS] + "\n\n[...truncated]"

    messages = [
        {"role": "system", "content": ASSUMPTION_CHECK_SYSTEM},
        {
            "role": "user",
            "content": assumption_check_user(
                structure.title, sections_text, calibration=calibration
            ),
        },
    ]

    try:
        result = client.complete(
            messages,
            OverviewFeedback,
            max_tokens=2048,
            temperature=_OVERVIEW_TEMPERATURE,
        )
        return list(result.issues)
    except Exception:
        logger.warning("Assumption checker failed, skipping")
        return []


def merge_overview(
    overview: OverviewFeedback,
    extra_issues: list[OverviewIssue],
    max_total: int = 8,
) -> OverviewFeedback:
    """Merge extra issues into overview, deduplicating by title similarity.

    Caps total at max_total issues. Dedup uses simple word overlap.
    """
    if not extra_issues:
        return overview

    existing_titles = {_normalize_title(i.title) for i in overview.issues}
    merged = list(overview.issues)

    for issue in extra_issues:
        norm = _normalize_title(issue.title)
        # Skip if similar title already exists
        if any(_title_overlap(norm, existing) > 0.5 for existing in existing_titles):
            continue
        if len(merged) >= max_total:
            break
        merged.append(issue)
        existing_titles.add(norm)

    return overview.model_copy(update={"issues": merged})


def _normalize_title(title: str) -> str:
    """Lowercase, strip punctuation for comparison."""
    return "".join(c for c in title.lower() if c.isalnum() or c == " ").strip()


def _title_overlap(a: str, b: str) -> float:
    """Word-level Jaccard similarity between two normalized titles."""
    from coarse.quote_verify import _jaccard

    return _jaccard(set(a.split()), set(b.split()))
