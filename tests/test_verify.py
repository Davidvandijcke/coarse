"""Tests for ProofVerifyAgent."""

from __future__ import annotations

from unittest.mock import MagicMock

from coarse.agents.verify import ProofVerifyAgent, _VerifiedComments
from coarse.types import DetailedComment, SectionInfo, SectionType


def _make_section(text: str = "Proof of Theorem 1. We show that X = Y. QED.") -> SectionInfo:
    return SectionInfo(
        number=3,
        title="Proofs",
        text=text,
        section_type=SectionType.APPENDIX,
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote="We show that X = Y by direct calculation.",
        feedback="The derivation skips a step.",
    )


def _make_agent(return_comments: list[DetailedComment] | None = None) -> ProofVerifyAgent:
    client = MagicMock()
    if return_comments is None:
        return_comments = [_make_comment(1)]
    client.complete.return_value = _VerifiedComments(comments=return_comments)
    return ProofVerifyAgent(client)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_proof_verify_agent_returns_comments():
    """Agent returns list[DetailedComment] from LLM response."""
    expected = [_make_comment(1), _make_comment(2)]
    agent = _make_agent(return_comments=expected)

    result = agent.run(
        _make_section(),
        "Test Paper",
        [_make_comment(1)],
        abstract="An abstract.",
    )

    assert len(result) == 2
    assert all(isinstance(c, DetailedComment) for c in result)


def test_proof_verify_agent_receives_first_pass():
    """User prompt sent to LLM includes first-pass comment text."""
    agent = _make_agent()
    first_pass = [_make_comment(1)]

    agent.run(_make_section(), "Test Paper", first_pass, abstract="An abstract.")

    call_args = agent.client.complete.call_args
    messages = call_args[0][0]
    user_msg = messages[-1]["content"]
    assert "First-Pass Comment 1" in user_msg
    assert "The derivation skips a step." in user_msg


def test_proof_verify_agent_truncates_long_sections():
    """Section text > MAX_SECTION_CHARS gets truncated."""
    agent = _make_agent()
    long_text = "x" * 600_000
    section = _make_section(text=long_text)

    agent.run(section, "Test Paper", [_make_comment(1)])

    call_args = agent.client.complete.call_args
    messages = call_args[0][0]
    user_msg = messages[-1]["content"]
    assert "[...truncated]" in user_msg
    # Original section object not mutated
    assert len(section.text) == 600_000


def test_proof_verify_agent_author_notes_prepend_to_user_message():
    agent = _make_agent()

    agent.run(
        _make_section(),
        "Test Paper",
        [_make_comment(1)],
        author_notes="focus on the identification proof in this section",
    )

    messages = agent.client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    user_content = [m for m in messages if m["role"] == "user"][0]["content"]

    assert "focus on the identification proof in this section" not in system_content
    assert "<author_notes>" in user_content
    assert "focus on the identification proof in this section" in user_content


def _make_noncaching_agent() -> ProofVerifyAgent:
    """Like _make_agent but with supports_prompt_caching=False so the
    system prompt lands as a plain string, not an Anthropic cache-control
    list wrapper."""
    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _VerifiedComments(comments=[_make_comment(1)])
    return ProofVerifyAgent(client)


def test_verify_agent_manuscript_system_prompt_unchanged():
    """Manuscript path: system prompt is byte-identical to PROOF_VERIFY_SYSTEM."""
    from coarse.prompts import PROOF_VERIFY_SYSTEM

    agent = _make_noncaching_agent()
    agent.run(_make_section(), "Title", [_make_comment(1)])

    messages = agent.client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content == PROOF_VERIFY_SYSTEM


def test_verify_agent_outline_gets_form_notice():
    """An outline with a Proof section stub should not trigger the full
    adversarial verifier frame. The form notice relaxes the prompt."""
    from coarse.prompts import PROOF_VERIFY_SYSTEM

    agent = _make_noncaching_agent()
    agent.run(_make_section(), "Title", [_make_comment(1)], document_form="outline")

    messages = agent.client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content.startswith(PROOF_VERIFY_SYSTEM)
    assert "DOCUMENT FORM: OUTLINE" in system_content
