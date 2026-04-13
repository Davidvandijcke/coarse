"""Overview agent — produces macro-level OverviewFeedback from a PaperStructure."""

from __future__ import annotations

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import (
    OVERVIEW_SYSTEM,
    author_notes_block,
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
)

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
        author_notes: str | None = None,
    ) -> OverviewFeedback:
        sections_text = _build_sections_text(structure.sections)

        # Append the document-form addendum to the system prompt. Empty string
        # for manuscripts/preprints so that path is unchanged; a tailored block
        # for outlines/drafts/proposals/etc. that relaxes the peer-review frame.
        system_prompt = OVERVIEW_SYSTEM + document_form_notice(structure.document_form)

        # Author steering notes — returns "" when notes is None/empty so the
        # no-notes path is byte-identical. Prepended to the user message only,
        # so the cached system block is unchanged.
        notes_prefix = author_notes_block(author_notes)

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
                    "content": notes_prefix
                    + overview_user(
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
                    "content": notes_prefix
                    + overview_user(
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
