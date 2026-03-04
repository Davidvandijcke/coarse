"""Structure analysis for coarse.

Parses Docling-produced markdown to extract paper structure: sections are
identified by heading hierarchy, section text is a direct substring of
full_markdown. Domain/taxonomy classification is a cheap text-LLM call.
"""
from __future__ import annotations

import logging
import re

from coarse.llm import LLMClient
from coarse.prompts import METADATA_SYSTEM
from coarse.types import (
    PaperMetadata,
    PaperStructure,
    PaperText,
    SectionInfo,
    SectionType,
)

logger = logging.getLogger(__name__)

# Map heading title keywords to SectionType
_TYPE_KEYWORDS: dict[str, SectionType] = {
    "abstract": SectionType.ABSTRACT,
    "introduction": SectionType.INTRODUCTION,
    "related work": SectionType.RELATED_WORK,
    "literature": SectionType.RELATED_WORK,
    "prior work": SectionType.RELATED_WORK,
    "background": SectionType.RELATED_WORK,
    "method": SectionType.METHODOLOGY,
    "methodology": SectionType.METHODOLOGY,
    "approach": SectionType.METHODOLOGY,
    "model": SectionType.METHODOLOGY,
    "identification": SectionType.METHODOLOGY,
    "estimation": SectionType.METHODOLOGY,
    "result": SectionType.RESULTS,
    "finding": SectionType.RESULTS,
    "experiment": SectionType.RESULTS,
    "simulation": SectionType.RESULTS,
    "empirical": SectionType.RESULTS,
    "discussion": SectionType.DISCUSSION,
    "conclusion": SectionType.CONCLUSION,
    "concluding": SectionType.CONCLUSION,
    "summary": SectionType.CONCLUSION,
    "appendix": SectionType.APPENDIX,
    "supplementary": SectionType.APPENDIX,
    "reference": SectionType.REFERENCES,
    "bibliography": SectionType.REFERENCES,
}

# Regex for markdown headings: # through ####
_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)


def analyze_structure(paper_text: PaperText, client: LLMClient) -> PaperStructure:
    """Extract paper structure by parsing markdown headings + cheap LLM metadata call.

    1. Parse headings from Docling markdown to build sections
    2. Extract title from first heading
    3. Extract abstract from first ABSTRACT section or first paragraph
    4. Get domain/taxonomy via cheap text-LLM call
    """
    sections = _parse_sections_from_markdown(paper_text.full_markdown)
    title = _extract_title(paper_text.full_markdown)
    abstract = _extract_abstract(sections, paper_text.full_markdown)

    headings = [s.title for s in sections]
    metadata = _get_metadata(title, abstract, headings, client)

    return PaperStructure(
        title=title,
        domain=metadata.domain,
        taxonomy=metadata.taxonomy,
        abstract=abstract,
        sections=sections,
    )


def _parse_sections_from_markdown(markdown: str) -> list[SectionInfo]:
    """Parse markdown headings to build section list.

    Each section's text is the substring of full_markdown between consecutive
    headings, ensuring section quotes are always substrings of full_markdown.
    """
    matches = list(_HEADING_RE.finditer(markdown))
    if not matches:
        # No headings found — treat entire document as one section
        return [SectionInfo(
            number=1,
            title="Full Document",
            text=markdown.strip(),
            section_type=SectionType.OTHER,
        )]

    sections: list[SectionInfo] = []
    for i, match in enumerate(matches):
        level = len(match.group(1))
        title = match.group(2).strip()

        # Section text: from end of this heading line to start of next heading (or EOF)
        text_start = match.end()
        text_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        text = markdown[text_start:text_end].strip()

        # Derive section number from position
        number: int | float | str = i + 1

        section_type = _classify_section_type(title)

        sections.append(SectionInfo(
            number=number,
            title=title,
            text=text,
            section_type=section_type,
        ))

    return sections


def _classify_section_type(title: str) -> SectionType:
    """Classify section type from heading title using keyword matching."""
    title_lower = title.lower()
    for keyword, section_type in _TYPE_KEYWORDS.items():
        if keyword in title_lower:
            return section_type
    return SectionType.OTHER


def _extract_title(markdown: str) -> str:
    """Extract paper title from the first heading or first line."""
    match = _HEADING_RE.search(markdown)
    if match:
        return match.group(2).strip()
    # Fallback: first non-empty line
    for line in markdown.split("\n"):
        line = line.strip()
        if line:
            return line
    return "Untitled"


def _extract_abstract(sections: list[SectionInfo], markdown: str) -> str:
    """Extract abstract from sections or first paragraph of markdown."""
    for section in sections:
        if section.section_type == SectionType.ABSTRACT:
            return section.text[:2000]

    # Fallback: first paragraph (text before any heading)
    match = _HEADING_RE.search(markdown)
    if match and match.start() > 0:
        return markdown[:match.start()].strip()[:2000]

    # Last resort: first 500 chars
    return markdown[:500].strip()


def _get_metadata(
    title: str,
    abstract: str,
    headings: list[str],
    client: LLMClient,
) -> PaperMetadata:
    """Cheap text-LLM call for domain/taxonomy classification (~$0.001)."""
    headings_str = ", ".join(headings[:20])
    messages = [
        {"role": "system", "content": METADATA_SYSTEM},
        {"role": "user", "content": (
            f"Classify this paper.\n\n"
            f"**Title**: {title}\n"
            f"**Abstract**: {abstract[:1000]}\n"
            f"**Headings**: {headings_str}\n"
        )},
    ]
    try:
        return client.complete(messages, PaperMetadata, max_tokens=256, temperature=0.1)
    except Exception:
        logger.warning("Metadata classification failed, using defaults")
        return PaperMetadata(domain="unknown", taxonomy="academic/research_paper")
