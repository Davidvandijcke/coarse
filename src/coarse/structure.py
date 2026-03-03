"""Structure analysis for coarse.

Calls the LLM to parse a research paper's structure from its extracted text,
then fills in full section text from the source document.
"""
from __future__ import annotations

import re

from coarse.llm import LLMClient
from coarse.prompts import STRUCTURE_SYSTEM, structure_user
from coarse.types import PaperStructure, PaperText


def analyze_structure(paper_text: PaperText, client: LLMClient) -> PaperStructure:
    """Parse PaperText into PaperStructure via a single structured LLM call.

    The LLM returns only metadata and first sentences per section.
    Full section text is then populated from the source markdown.
    """
    messages = [
        {"role": "system", "content": STRUCTURE_SYSTEM},
        {"role": "user", "content": structure_user(paper_text.full_markdown)},
    ]
    structure = client.complete(
        messages,
        PaperStructure,
        max_tokens=8192,
        temperature=0.1,
    )
    _fill_section_text(structure, paper_text.full_markdown)
    return structure


def _fill_section_text(structure: PaperStructure, full_markdown: str) -> None:
    """Populate each section's text field from the source markdown.

    Finds each section heading in the source and extracts text up to the next heading.
    Falls back to the LLM-provided text if heading not found.
    """
    sections = structure.sections
    if not sections:
        return

    # First, find all markdown headings in the source
    # Match lines that look like headings: ## Title, **Title**, or numbered sections
    heading_re = re.compile(
        r"(?m)^(?:#{1,6}\s+|(?:\*\*))(.+?)(?:\*\*)?\s*$"
    )
    source_headings: list[tuple[str, int, int]] = []  # (title, start, end)
    for m in heading_re.finditer(full_markdown):
        source_headings.append((m.group(1).strip(), m.start(), m.end()))

    # Match each section to the best source heading
    heading_positions: list[tuple[int, int]] = []
    for sec in sections:
        best_match = _find_best_heading(sec.title, source_headings)
        if best_match is not None:
            heading_positions.append((best_match[1], best_match[2]))
        else:
            heading_positions.append((-1, -1))

    for i, sec in enumerate(sections):
        start, hdr_end = heading_positions[i]
        if start < 0:
            continue

        # Find end: next section's heading start, or end of document
        end = len(full_markdown)
        for j in range(i + 1, len(sections)):
            next_start, _ = heading_positions[j]
            if next_start > hdr_end:
                end = next_start
                break

        sec.text = full_markdown[hdr_end:end].strip()


def _normalize_title(title: str) -> str:
    """Normalize a title for fuzzy comparison."""
    # Remove accents, special chars, extra whitespace; lowercase
    title = title.lower().strip()
    title = re.sub(r"[´`''′]", "", title)  # accent marks
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"[^a-z0-9 ]", "", title)
    return title


def _find_best_heading(
    target: str, headings: list[tuple[str, int, int]]
) -> tuple[str, int, int] | None:
    """Find the source heading that best matches the target title."""
    norm_target = _normalize_title(target)
    if not norm_target:
        return None

    best = None
    best_score = 0.0
    for title, start, end in headings:
        norm_source = _normalize_title(title)
        if not norm_source:
            continue
        # Check substring match (either direction)
        if norm_target in norm_source or norm_source in norm_target:
            score = min(len(norm_target), len(norm_source)) / max(
                len(norm_target), len(norm_source)
            )
            if score > best_score:
                best_score = score
                best = (title, start, end)
        # Also check if target words appear in source
        elif best is None:
            target_words = set(norm_target.split())
            source_words = set(norm_source.split())
            if target_words and source_words:
                overlap = len(target_words & source_words) / len(target_words)
                if overlap > 0.6 and overlap > best_score:
                    best_score = overlap
                    best = (title, start, end)

    return best
