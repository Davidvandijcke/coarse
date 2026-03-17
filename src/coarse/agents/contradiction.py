"""Contradiction check agent — flags comments that contradict the paper's stated contribution."""
from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.prompts import CONTRADICTION_CHECK_SYSTEM, contradiction_check_user
from coarse.types import ContributionContext, DetailedComment

_TEMPERATURE = 0.1


class _CheckedComments(BaseModel):
    """Response envelope for checked comments."""
    comments: list[DetailedComment]


class ContradictionCheckAgent(ReviewAgent):
    """Flags comments that contradict the paper's stated contributions.

    Flagged comments get confidence downgraded to "low" with a note
    explaining the consistency concern. Unflagged comments pass through.
    """

    def run(  # type: ignore[override]
        self,
        abstract: str,
        contribution_context: ContributionContext | None,
        comments: list[DetailedComment],
    ) -> list[DetailedComment]:
        user_text = contradiction_check_user(abstract, contribution_context, comments)
        messages = self._build_messages(CONTRADICTION_CHECK_SYSTEM, user_text)
        result = self.client.complete(
            messages, _CheckedComments, max_tokens=16384, temperature=_TEMPERATURE
        )
        return result.comments
