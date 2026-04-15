"""Section agent — produces DetailedComments for a single paper section."""

from __future__ import annotations

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent, truncate_section
from coarse.prompts import (
    SECTION_SYSTEM,
    SECTION_SYSTEM_MAP,
    author_notes_block,
    document_form_notice,
    section_user,
)
from coarse.types import (
    DetailedComment,
    DocumentForm,
    DomainCalibration,
    OverviewFeedback,
    SectionInfo,
)

_TEMPERATURE = 0.3


class _SectionComments(BaseModel):
    """Instructor response envelope for section-level detailed comments.

    ``comments`` is allowed to be empty: a given section may legitimately
    have zero issues worth flagging, and every other agent envelope in
    this package (``_VerifiedComments``, ``_CheckedComments``,
    ``_RevisedComments``, ``_CrossSectionComments``,
    ``_ConsolidatedComments``, ``_EditorialComments``) already uses the
    same zero-or-more contract. Before the constraint was dropped, cheap
    models running at ``--effort low`` would occasionally return an
    empty list three times in a row, the schema would reject it as
    ``List should have at least 1 item``, the retry loop in
    ``headless_clients.py`` (and instructor on the hosted path) would
    exhaust after 3 attempts, and the pipeline would skip the entire
    section's comments instead of treating ``[]`` as a valid no-op.
    See ``review_stages._review_section`` — it already guards proof
    verification with ``if ... and comments and ...`` so the downstream
    path tolerates an empty list without any other changes.
    """

    comments: list[DetailedComment] = Field(default_factory=list)


class SectionAgent(ReviewAgent):
    """Produces DetailedComments for a single paper section.

    Contract: comment numbers are local (1-N within this section).
    The crossref agent is responsible for global renumbering.
    """

    def run(  # type: ignore[override]
        self,
        section: SectionInfo,
        paper_title: str,
        overview: "OverviewFeedback | None" = None,
        calibration: "DomainCalibration | None" = None,
        focus: str = "general",
        literature_context: str = "",
        all_sections: "list[SectionInfo] | None" = None,
        abstract: str = "",
        document_form: DocumentForm = "manuscript",
        author_notes: str | None = None,
    ) -> list[DetailedComment]:
        truncated = truncate_section(section)

        # Append form-specific addendum to the focus-selected system prompt.
        # Empty for manuscript/preprint so the default peer-review path is
        # unchanged.
        base_system = SECTION_SYSTEM_MAP.get(focus, SECTION_SYSTEM)
        system_prompt = base_system + document_form_notice(document_form)
        user_text = author_notes_block(author_notes) + section_user(
            paper_title,
            truncated,
            overview=overview,
            calibration=calibration,
            literature_context=literature_context,
            all_sections=all_sections,
            abstract=abstract,
        )

        messages = self._build_messages(system_prompt, user_text)

        result = self.client.complete(
            messages, _SectionComments, max_tokens=16384, temperature=_TEMPERATURE
        )
        return result.comments
