"""Cross-section synthesis agent — checks discussion claims against formal results."""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent, truncate_section
from coarse.prompts import (
    CROSS_SECTION_SYSTEM,
    author_notes_block,
    cross_section_user,
    document_form_notice,
)
from coarse.types import DetailedComment, DocumentForm, SectionInfo

logger = logging.getLogger(__name__)

_TEMPERATURE = 0.3


class _CrossSectionComments(BaseModel):
    comments: list[DetailedComment] = Field(default_factory=list)


class CrossSectionAgent(ReviewAgent):
    """Checks whether discussion/implications are supported by formal results."""

    def run(  # type: ignore[override]
        self,
        paper_title: str,
        results_section: SectionInfo,
        discussion_section: SectionInfo,
        abstract: str = "",
        document_form: DocumentForm = "manuscript",
        author_notes: str | None = None,
    ) -> list[DetailedComment]:
        results_section = truncate_section(results_section)
        discussion_section = truncate_section(discussion_section)

        user_text = author_notes_block(author_notes) + cross_section_user(
            paper_title,
            results_section,
            discussion_section,
            abstract=abstract,
        )
        # Empty notice for manuscript so manuscript path is byte-identical.
        system_prompt = CROSS_SECTION_SYSTEM + document_form_notice(document_form)
        messages = self._build_messages(system_prompt, user_text)
        result = self.client.complete(
            messages,
            _CrossSectionComments,
            max_tokens=8192,
            temperature=_TEMPERATURE,
        )
        return result.comments
