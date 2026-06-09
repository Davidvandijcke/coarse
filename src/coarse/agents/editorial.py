"""Editorial agent — merged filtering pass with full paper context.

Replaces the previous crossref → contradiction → critique pipeline with a single
LLM call that has access to the full paper text, overview issues, contribution
context, and all draft comments. Performs deduplication, contradiction checking,
quality filtering, severity assignment, notation capping, humanization, and
importance ordering in one pass.
"""

from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import (
    EDITORIAL_SYSTEM,
    author_notes_block,
    editorial_system,
    editorial_user,
    feedback_system_prompt,
)
from coarse.types import (
    ContributionContext,
    DetailedComment,
    DocumentForm,
    OverviewFeedback,
)

# 0.0: the editorial pass filters and consolidates an existing comment list —
# it is not generative, so determinism is preferable. The earlier 0.15 only
# added run-to-run variance that produced wildly different comment counts (e.g.
# ~80 lightly-deduped one run vs ~18 the next) for the same input (#200).
_TEMPERATURE = 0.0


class _EditorialComments(BaseModel):
    """Instructor response envelope for the editorially filtered comment list."""

    comments: list[DetailedComment]


class EditorialAgent(ReviewAgent):
    """Single-pass editorial filter that replaces crossref + contradiction + critique.

    Receives the full paper text so it can verify quotes, check absence claims,
    and make informed filtering decisions.
    """

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(  # type: ignore[override]
        self,
        paper_text: str,
        overview: OverviewFeedback,
        comments: list[DetailedComment],
        comment_target: int | str | None = None,
        title: str = "",
        abstract: str = "",
        contribution_context: ContributionContext | None = None,
        document_form: DocumentForm = "manuscript",
        author_notes: str | None = None,
    ) -> list[DetailedComment]:
        user_content = author_notes_block(author_notes) + editorial_user(
            paper_text,
            overview,
            comments,
            title=title,
            abstract=abstract,
            contribution_context=contribution_context,
        )
        base_sys = editorial_system(comment_target) if comment_target else EDITORIAL_SYSTEM
        # Append form-specific addendum (empty for manuscript/preprint) so the
        # editorial pass also relaxes its framing on non-manuscript inputs.
        sys_prompt = feedback_system_prompt(base_sys, document_form)

        messages = self._build_messages(sys_prompt, user_content)
        result = self.client.complete(
            messages, _EditorialComments, max_tokens=32768, temperature=_TEMPERATURE
        )
        return result.comments
