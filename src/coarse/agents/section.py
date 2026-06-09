"""Section agent — produces DetailedComments for a single paper section."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field

from coarse.agents.base import ReviewAgent, truncate_section
from coarse.prompts import (
    SECTION_SYSTEM,
    SECTION_SYSTEM_MAP,
    author_notes_block,
    feedback_system_prompt,
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

# A quote that is nothing but LaTeX control sequences — table rules like
# \cmidrule(lr){2-5}, \toprule, \hline, \begin/\end, spacing commands — is a
# useless anchor: it carries no reviewable prose and cannot satisfy the
# >=20-char verbatim-quote contract on DetailedComment.quote.
_LATEX_ONLY_QUOTE_RE = re.compile(r"^(?:\\[A-Za-z@]+\*?(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\})*\s*)+$")


def _is_low_value_quote(quote: str) -> bool:
    """True for a quote that should be dropped rather than anchored to a comment.

    Catches the two shapes that break the ``DetailedComment.quote`` contract:
    anything under 20 characters once stripped, and a bare run of LaTeX control
    tokens with no prose (e.g. ``\\cmidrule(lr){2-5}``, 18 chars). See
    ``_LooseSectionComment`` for why this filtering happens here (#198).
    """
    q = quote.strip()
    return len(q) < 20 or bool(_LATEX_ONLY_QUOTE_RE.match(q))


class _LooseSectionComment(DetailedComment):
    """Section-agent response shape with the 20-char quote floor relaxed (#198).

    The model occasionally picks a short or bare-LaTeX-token quote (e.g.
    ``\\cmidrule(lr){2-5}``). Under the strict ``DetailedComment`` schema that
    fails ``min_length=20``, and because instructor validates the whole batch,
    one bad quote triggers a retry storm that on exhaustion drops the ENTIRE
    section (``pipeline`` skips a section whose agent raises). Relaxing the
    floor here lets the batch parse; ``SectionAgent.run`` then drops the
    low-value comment(s) and re-validates the survivors as strict
    ``DetailedComment`` instances, so downstream consumers see only valid
    >=20-char quotes.
    """

    # The LLM/JSON path validates dicts (no config needed); from_attributes
    # additionally lets the envelope be built from existing DetailedComment
    # instances (the parent class), which in-memory callers and the test
    # helpers do — without it, `_SectionComments(comments=[DetailedComment(...)])`
    # raises model_type.
    model_config = ConfigDict(from_attributes=True)

    quote: str = Field(min_length=1, description="Verbatim quote from the paper")


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

    comments: list[_LooseSectionComment] = Field(default_factory=list)


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
        system_prompt = feedback_system_prompt(base_system, document_form)
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
        # Drop low-value quotes (too short / bare LaTeX tokens) and re-validate
        # survivors as strict DetailedComments. See _LooseSectionComment (#198).
        return [
            DetailedComment.model_validate(c.model_dump())
            for c in result.comments
            if not _is_low_value_quote(c.quote)
        ]
