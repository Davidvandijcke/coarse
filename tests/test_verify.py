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
        _make_section(), "Test Paper", [_make_comment(1)], abstract="An abstract.",
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
