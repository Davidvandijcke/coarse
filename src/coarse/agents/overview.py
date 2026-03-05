"""Overview agent — produces macro-level OverviewFeedback from a PaperStructure."""
from __future__ import annotations

import logging

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import (
    ASSUMPTION_CHECK_SYSTEM,
    OVERVIEW_PERSONAS,
    OVERVIEW_SYNTHESIS_SYSTEM,
    OVERVIEW_SYSTEM,
    assumption_check_user,
    overview_synthesis_user,
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

# Maximum total characters sent to the overview agent.
MAX_OVERVIEW_CHARS = 500_000

# Section types that get full text (theory-heavy, high-value for cross-cutting analysis).
_FULL_TEXT_TYPES = {
    SectionType.METHODOLOGY,
    SectionType.RESULTS,
    SectionType.DISCUSSION,
    SectionType.APPENDIX,
    SectionType.OTHER,
}

# Section types that get truncated (context only, not where the substance lives).
_TRUNCATED_LIMIT = 10_000


def _build_sections_summary(sections: list[SectionInfo]) -> str:
    """Convert sections list to a text block for the overview prompt.

    Methodology, results, discussion, and appendix sections get full text.
    Introduction, conclusion, and related_work get truncated to 2000 chars.
    Total output is capped at MAX_OVERVIEW_CHARS with proportional allocation.
    """
    # Phase 1: Build raw parts with full or truncated text
    raw_parts: list[tuple[str, int]] = []  # (text, weight)
    for sec in sections:
        if not sec.text:
            header = f"## {sec.number}. {sec.title} ({sec.section_type.value})\n(empty)"
            raw_parts.append((header, 1))
            continue

        if sec.section_type in _FULL_TEXT_TYPES:
            body = sec.text
            weight = 2  # methodology/results get 2x budget in proportional allocation
        else:
            body = sec.text[:_TRUNCATED_LIMIT]
            if len(sec.text) > _TRUNCATED_LIMIT:
                body += "\n[...truncated]"
            weight = 1

        header = f"## {sec.number}. {sec.title} ({sec.section_type.value})\n{body}"
        raw_parts.append((header, weight))

    # Phase 2: Check total length, proportionally truncate if over budget
    total_len = sum(len(text) for text, _ in raw_parts)
    if total_len <= MAX_OVERVIEW_CHARS:
        return "\n\n".join(text for text, _ in raw_parts)

    # Proportional allocation: each part gets chars proportional to its weight
    total_weight = sum(w for _, w in raw_parts)
    final_parts = []
    for text, weight in raw_parts:
        budget = int(MAX_OVERVIEW_CHARS * weight / total_weight)
        if len(text) > budget:
            text = text[:budget] + "\n[...truncated to fit budget]"
        final_parts.append(text)

    return "\n\n".join(final_parts)


class OverviewAgent(ReviewAgent):
    """Produces 4-6 macro-level issues from a PaperStructure."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        structure: PaperStructure,
        calibration: DomainCalibration | None = None,
        persona: str | None = None,
        literature_context: str = "",
    ) -> OverviewFeedback:
        sections_summary = _build_sections_summary(structure.sections)
        system = (persona + "\n\n" + OVERVIEW_SYSTEM) if persona else OVERVIEW_SYSTEM
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": overview_user(
                    structure.title, structure.abstract,
                    sections_summary, calibration=calibration,
                    literature_context=literature_context,
                ),
            },
        ]
        return self.client.complete(  # type: ignore[return-value]
            messages, OverviewFeedback, max_tokens=4096, temperature=0.3
        )

    def run_panel(
        self,
        structure: PaperStructure,
        calibration: DomainCalibration | None = None,
        literature_context: str = "",
    ) -> OverviewFeedback:
        """Run 3 judges in parallel with different personas, then synthesize."""
        from concurrent.futures import ThreadPoolExecutor

        overviews: list[OverviewFeedback] = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    self.run, structure, calibration, persona, literature_context
                )
                for persona in OVERVIEW_PERSONAS
            ]
            for i, future in enumerate(futures):
                try:
                    overviews.append(future.result())
                except Exception:
                    logger.warning("Overview judge %d failed, skipping", i)

        if not overviews:
            raise RuntimeError("All overview judges failed")
        if len(overviews) == 1:
            return overviews[0]

        return synthesize_overviews(overviews, self.client)


def synthesize_overviews(
    overviews: list[OverviewFeedback],
    client: LLMClient,
) -> OverviewFeedback:
    """Synthesize multiple overview assessments into a single consolidated overview."""
    messages = [
        {"role": "system", "content": OVERVIEW_SYNTHESIS_SYSTEM},
        {"role": "user", "content": overview_synthesis_user(overviews)},
    ]
    return client.complete(  # type: ignore[return-value]
        messages, OverviewFeedback, max_tokens=4096, temperature=0.2
    )


# Section types relevant for assumption checking
_ASSUMPTION_RELEVANT_TYPES = {
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

    Extracts methodology and empirical sections, sends to LLM for consistency check.
    Returns 0-3 OverviewIssue objects.
    """
    relevant_sections = [
        s for s in structure.sections
        if s.section_type in _ASSUMPTION_RELEVANT_TYPES and len(s.text) > 50
    ]
    if not relevant_sections:
        return []

    # Build condensed text from relevant sections (cap at 40K chars)
    sections_text = "\n\n".join(
        f"## {s.number}. {s.title}\n{s.text}" for s in relevant_sections
    )
    if len(sections_text) > 500_000:
        sections_text = sections_text[:500_000] + "\n\n[...truncated]"

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
        result = client.complete(messages, OverviewFeedback, max_tokens=2048, temperature=0.3)
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

    return OverviewFeedback(issues=merged)


def _normalize_title(title: str) -> str:
    """Lowercase, strip punctuation for comparison."""
    return "".join(c for c in title.lower() if c.isalnum() or c == " ").strip()


def _title_overlap(a: str, b: str) -> float:
    """Word-level Jaccard similarity between two normalized titles."""
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)
