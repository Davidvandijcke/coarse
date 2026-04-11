"""Proof verification agent — adversarial second pass on proof sections."""

from __future__ import annotations

from pydantic import BaseModel

from coarse.agents.base import ReviewAgent, truncate_section
from coarse.prompts import PROOF_VERIFY_SYSTEM, document_form_notice, proof_verify_user
from coarse.types import DetailedComment, DocumentForm, SectionInfo

_TEMPERATURE = 0.2


class _VerifiedComments(BaseModel):
    """Response envelope for verified + new comments."""

    comments: list[DetailedComment]


class ProofVerifyAgent(ReviewAgent):
    """Adversarial verification of proof sections.

    Receives a proof section + first-pass comments. Validates existing
    findings via independent re-derivation, generates counterexamples,
    and checks for missed issues.
    """

    def run(  # type: ignore[override]
        self,
        section: SectionInfo,
        paper_title: str,
        first_pass_comments: list[DetailedComment],
        abstract: str = "",
        document_form: DocumentForm = "manuscript",
    ) -> list[DetailedComment]:
        section = truncate_section(section)

        user_text = proof_verify_user(
            paper_title,
            section,
            first_pass_comments,
            abstract=abstract,
        )
        # Append form-specific addendum (empty for manuscript) so an outline
        # or partial draft whose "Proof" heading contains stub text doesn't
        # trigger the full adversarial verifier frame.
        system_prompt = PROOF_VERIFY_SYSTEM + document_form_notice(document_form)
        messages = self._build_messages(system_prompt, user_text)
        result = self.client.complete(
            messages,
            _VerifiedComments,
            max_tokens=16384,
            temperature=_TEMPERATURE,
        )
        return result.comments
