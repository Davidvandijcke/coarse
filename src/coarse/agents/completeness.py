"""Completeness agent — identifies structural gaps and missing content."""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import (
    COMPLETENESS_SYSTEM,
    author_notes_block,
    completeness_user,
    document_form_notice,
)
from coarse.review_utils import build_sections_text
from coarse.types import (
    ContributionContext,
    DomainCalibration,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
)

logger = logging.getLogger(__name__)

_COMPLETENESS_TEMPERATURE = 0.5

# Document forms for which "flag missing content" is noise by construction:
# an outline is ~100% missing content, notes are not papers, "other" documents
# are not being peer-reviewed. Skip the completeness agent entirely for these
# rather than running it with a diluted prompt. draft/proposal/report still
# run because partial drafts and proposals benefit from "you haven't addressed
# X yet" feedback.
_SKIP_COMPLETENESS_FORMS = frozenset({"outline", "notes", "other"})


class _CompletenessResult(BaseModel):
    """Response model for completeness agent (allows 0 issues)."""

    issues: list[OverviewIssue] = Field(default_factory=list)


class CompletenessAgent(ReviewAgent):
    """Identifies structural gaps — missing examples, simulations, implications."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        structure: PaperStructure,
        overview: OverviewFeedback,
        calibration: DomainCalibration | None = None,
        contribution_context: ContributionContext | None = None,
        author_notes: str | None = None,
    ) -> list[OverviewIssue]:
        # Short-circuit for document forms where "flag missing content" is
        # meaningless: outlines ARE missing content on purpose, notes aren't
        # papers, and "other" isn't a peer-review target. Drafts and proposals
        # still run — partial drafts benefit from "you haven't addressed X".
        if structure.document_form in _SKIP_COMPLETENESS_FORMS:
            logger.info(
                "Skipping completeness agent for document_form=%s",
                structure.document_form,
            )
            return []

        sections_text = build_sections_text(structure.sections)

        user_text = author_notes_block(author_notes) + completeness_user(
            structure.title,
            structure.abstract,
            sections_text,
            overview,
            calibration=calibration,
            contribution_context=contribution_context,
        )
        # Append form-specific addendum (empty for manuscript/preprint).
        system_prompt = COMPLETENESS_SYSTEM + document_form_notice(structure.document_form)
        messages = self._build_messages(system_prompt, user_text)

        result = self.client.complete(
            messages,
            _CompletenessResult,
            max_tokens=4096,
            temperature=_COMPLETENESS_TEMPERATURE,
        )
        return list(result.issues)
