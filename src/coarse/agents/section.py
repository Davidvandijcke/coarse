"""Section agent — produces DetailedComments for a single paper section."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import SECTION_SYSTEM, section_user
from coarse.types import DetailedComment, SectionInfo

if TYPE_CHECKING:
    from coarse.types import PaperText


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

    # Max page images to include per section in vision mode
    MAX_VISION_PAGES = 4

    def run(  # type: ignore[override]
        self,
        section: SectionInfo,
        paper_title: str,
        paper_text: "PaperText | None" = None,
    ) -> list[DetailedComment]:
        # Truncate very long sections to avoid token overflow
        if len(section.text) > self.MAX_SECTION_CHARS:
            truncated = section.model_copy(
                update={"text": section.text[: self.MAX_SECTION_CHARS] + "\n\n[...truncated]"}
            )
        else:
            truncated = section

        user_text = section_user(paper_title, truncated)

        # Build multimodal message if page images are available
        page_images = _find_section_pages(truncated, paper_text) if paper_text else []
        if page_images:
            content: list[dict] = [{"type": "text", "text": user_text}]
            for img_b64 in page_images[: self.MAX_VISION_PAGES]:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                })
            messages = [
                {"role": "system", "content": SECTION_SYSTEM},
                {"role": "user", "content": content},
            ]
        else:
            messages = [
                {"role": "system", "content": SECTION_SYSTEM},
                {"role": "user", "content": user_text},
            ]

        result = self.client.complete(
            messages, _SectionComments, max_tokens=4096, temperature=0.3
        )
        return result.comments


def _find_section_pages(
    section: SectionInfo, paper_text: "PaperText | None"
) -> list[str]:
    """Find page images that overlap with the section text.

    Returns list of base64-encoded PNG strings for pages whose text
    contains part of the section's first ~200 chars.
    """
    if paper_text is None:
        return []

    # Only use pages that have images
    image_pages = [p for p in paper_text.pages if p.image_b64]
    if not image_pages:
        return []

    # Use first ~200 chars of section text as search snippet
    snippet = section.text[:200].strip()
    if len(snippet) < 20:
        return []

    # Search for pages containing words from the snippet
    snippet_words = set(snippet.lower().split()[:15])
    matches = []
    for page in image_pages:
        page_words = set(page.text.lower().split())
        overlap = len(snippet_words & page_words) / max(len(snippet_words), 1)
        if overlap > 0.4:
            matches.append((overlap, page))

    # Sort by overlap, take best matches
    matches.sort(key=lambda x: x[0], reverse=True)
    return [page.image_b64 for _, page in matches]
