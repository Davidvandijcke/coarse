"""Structure analysis for coarse.

Parses Docling-produced markdown to extract paper structure: sections are
identified by heading hierarchy, section text is a direct substring of
full_markdown. Domain/taxonomy classification is a cheap text-LLM call.
"""
from __future__ import annotations

import logging
import re

from coarse.llm import LLMClient
from coarse.prompts import MATH_DETECTION_SYSTEM, METADATA_SYSTEM, math_detection_user
from coarse.types import (
    MathSectionDetection,
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

# Regex to detect a formal statement header at the start of a paragraph
_FORMAL_HEADER_RE = re.compile(
    r"\*{0,2}"
    r"\b(Theorem|Lemma|Proposition|Corollary|Claim|Result"
    r"|Definition|Assumption|Condition|Axiom|Conjecture|Hypothesis)\b"
    r"\s*\*{0,2}"
    r"\s*"
    r"([A-Z]?\d*[a-z]?(?:\.\d+)?)",
    re.IGNORECASE,
)


def _extract_claims_and_definitions(text: str) -> tuple[list[str], list[str]]:
    """Extract formal claims and definitions from section text via regex.

    Splits text into paragraphs, finds formal statement headers, and
    extracts the statement body. Zero LLM cost — pure regex extraction.
    Returns (claims, definitions).
    """
    claims: list[str] = []
    definitions: list[str] = []

    paragraphs = re.split(r"\n\s*\n", text)
    for para in paragraphs:
        m = _FORMAL_HEADER_RE.search(para)
        if not m:
            continue

        kind = m.group(1).lower()
        label = m.group(2).strip()

        # Statement = everything after the header in this paragraph
        statement = para[m.end():].strip()
        # Strip leading punctuation, bold markers, whitespace
        statement = re.sub(r"^[.*:)\s]+", "", statement)

        short = statement[:500] + ("..." if len(statement) > 500 else "")
        entry = f"{m.group(1)} {label}: {short}".strip()

        if kind in ("definition", "axiom"):
            definitions.append(entry)
        else:
            claims.append(entry)

    return claims, definitions


def analyze_structure(paper_text: PaperText, client: LLMClient) -> PaperStructure:
    """Extract paper structure by parsing markdown headings + cheap LLM metadata call.

    1. Parse headings from Docling markdown to build sections
    2. Extract title from first heading
    3. Extract abstract from first ABSTRACT section or first paragraph
    4. Get domain/taxonomy via cheap text-LLM call
    5. Detect math sections via cheap LLM call
    """
    sections = _parse_sections_from_markdown(paper_text.full_markdown)
    heuristic_title = _extract_title(paper_text.full_markdown)
    abstract = _extract_abstract(sections, paper_text.full_markdown)

    headings = [s.title for s in sections]
    first_page = paper_text.full_markdown[:2000]
    metadata = _get_metadata(first_page, abstract, headings, client)

    title = metadata.title or heuristic_title

    # LLM-based math section detection
    sections = _detect_math_sections(sections, client)

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
        sec_claims, sec_defs = _extract_claims_and_definitions(text)

        sections.append(SectionInfo(
            number=number,
            title=title,
            text=text,
            section_type=section_type,
            claims=sec_claims,
            definitions=sec_defs,
        ))

    return sections


def _classify_section_type(title: str) -> SectionType:
    """Classify section type from heading title using keyword matching."""
    title_lower = title.lower()
    for keyword, section_type in _TYPE_KEYWORDS.items():
        if keyword in title_lower:
            return section_type
    return SectionType.OTHER


def _is_section_heading(title: str) -> bool:
    """Return True if the heading looks like a generic section name, not a paper title."""
    title_lower = title.lower().strip()
    # Strip leading numbering like "1.", "1.1", "A.", "I."
    title_lower = re.sub(r"^[\dA-Za-z]+[\.\)]\s*", "", title_lower).strip()
    return any(kw in title_lower for kw in _TYPE_KEYWORDS)


def _extract_title(markdown: str) -> str:
    """Extract paper title from headings or pre-heading text.

    Strategy:
    1. Find the first heading that is NOT a generic section name (abstract, etc.)
    2. If all headings are section names, use text before the first heading
    3. Fallback: first non-empty line
    """
    matches = list(_HEADING_RE.finditer(markdown))

    # Try first heading that isn't a section name
    for match in matches:
        candidate = match.group(2).strip()
        if not _is_section_heading(candidate):
            return candidate

    # All headings are section names — try text before the first heading
    if matches:
        preamble = markdown[:matches[0].start()].strip()
        if preamble:
            # Take the first non-empty line from the preamble
            for line in preamble.split("\n"):
                line = line.strip()
                if line and len(line) > 3:
                    return line

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
    first_page: str,
    abstract: str,
    headings: list[str],
    client: LLMClient,
) -> PaperMetadata:
    """Cheap text-LLM call for title extraction + domain/taxonomy classification (~$0.001)."""
    headings_str = ", ".join(headings[:20])
    messages = [
        {"role": "system", "content": METADATA_SYSTEM},
        {"role": "user", "content": (
            f"Extract the title and classify this paper.\n\n"
            f"**First page**:\n{first_page}\n\n"
            f"**Abstract**: {abstract[:1000]}\n"
            f"**Headings**: {headings_str}\n"
        )},
    ]
    try:
        return client.complete(messages, PaperMetadata, max_tokens=256, temperature=0.1)
    except Exception:
        logger.warning("Metadata extraction failed, using defaults")
        return PaperMetadata(
            title="", domain="unknown", taxonomy="academic/research_paper",
        )


# ---------------------------------------------------------------------------
# Math section detection
# ---------------------------------------------------------------------------

_PROOF_KEYWORDS = frozenset([
    "theorem", "proof", "lemma", "proposition", "corollary", "q.e.d", "qed",
    "∎", "□", "we prove", "we show that", "it follows that",
])


def _detect_math_sections_keyword(sections: list[SectionInfo]) -> list[SectionInfo]:
    """Keyword-based fallback for math detection."""
    result = []
    for s in sections:
        text_lower = s.text.lower()
        has_math = any(kw in text_lower for kw in _PROOF_KEYWORDS)
        result.append(s.model_copy(update={"math_content": True}) if has_math else s)
    return result


def _detect_math_sections(
    sections: list[SectionInfo],
    client: LLMClient,
) -> list[SectionInfo]:
    """Cheap LLM call to identify sections with math content (~$0.001).

    Returns new list with math_content flags set.
    Falls back to keyword detection on failure.
    """
    messages = [
        {"role": "system", "content": MATH_DETECTION_SYSTEM},
        {"role": "user", "content": math_detection_user(sections)},
    ]
    try:
        # max_tokens=1024 (not 256): Claude 4-family models sometimes write a
        # prose preamble before emitting the structured output. At 256 the
        # preamble alone can hit finish_reason='length' and instructor raises
        # InstructorRetryException("output is incomplete due to a max_tokens
        # length limit") before any JSON is produced. The actual indices
        # payload is tiny (<50 tokens), so the higher ceiling only costs more
        # when the model actually talks, which the prompt now discourages.
        result = client.complete(
            messages, MathSectionDetection, max_tokens=1024, temperature=0.1,
        )
        math_indices = set(result.math_section_indices)
    except Exception as exc:
        logger.warning(
            "Math section detection failed (%s: %s), falling back to keyword detection",
            type(exc).__name__, exc,
        )
        return _detect_math_sections_keyword(sections)

    return [
        s.model_copy(update={"math_content": True}) if i in math_indices else s
        for i, s in enumerate(sections)
    ]
