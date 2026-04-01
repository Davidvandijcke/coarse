"""Completeness agent — identifies structural gaps and missing content."""
from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent
from coarse.agents.overview import _build_sections_text
from coarse.llm import LLMClient
from coarse.prompts import COMPLETENESS_SYSTEM, completeness_user
from coarse.types import (
    ContributionContext,
    DomainCalibration,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
)

logger = logging.getLogger(__name__)

_COMPLETENESS_TEMPERATURE = 0.5


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
    ) -> list[OverviewIssue]:
        sections_text = _build_sections_text(structure.sections)

        user_text = completeness_user(
            structure.title,
            structure.abstract,
            sections_text,
            overview,
            calibration=calibration,
            contribution_context=contribution_context,
        )
        messages = self._build_messages(COMPLETENESS_SYSTEM, user_text)

        result = self.client.complete(
            messages, _CompletenessResult, max_tokens=4096,
            temperature=_COMPLETENESS_TEMPERATURE,
        )
        return list(result.issues)
