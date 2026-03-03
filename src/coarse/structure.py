"""Structure analysis for coarse.

Calls the LLM to parse a research paper's structure from its extracted text.
"""
from __future__ import annotations

from coarse.llm import LLMClient
from coarse.prompts import STRUCTURE_SYSTEM, structure_user
from coarse.types import PaperStructure, PaperText


def analyze_structure(paper_text: PaperText, client: LLMClient) -> PaperStructure:
    """Parse PaperText into PaperStructure via a single structured LLM call."""
    messages = [
        {"role": "system", "content": STRUCTURE_SYSTEM},
        {"role": "user", "content": structure_user(paper_text.full_markdown)},
    ]
    return client.complete(
        messages,
        PaperStructure,
        max_tokens=8192,
        temperature=0.1,
    )
