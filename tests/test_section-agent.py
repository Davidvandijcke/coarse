"""Tests for agents/section.py — SectionAgent."""
from unittest.mock import MagicMock

from coarse.agents.section import SectionAgent, _SectionComments
from coarse.llm import LLMClient
from coarse.types import (
    DetailedComment,
    SectionInfo,
    SectionType,
)


def _make_client() -> LLMClient:
    client = MagicMock(spec=LLMClient)
    client.supports_prompt_caching = False
    return client


def _make_section(
    number: int = 1,
    title: str = "Introduction",
    text: str = "This paper studies X. We find that Y causes Z.",
    section_type: SectionType = SectionType.INTRODUCTION,
    claims: list[str] | None = None,
) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=title,
        text=text,
        section_type=section_type,
        claims=claims or ["Claim 1", "Claim 2"],
        definitions=["Term A"],
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Issue {number}",
        quote="We find that Y causes Z.",
        feedback=f"Feedback for issue {number}.",
    )


def _make_section_comments(n: int) -> _SectionComments:
    return _SectionComments(comments=[_make_comment(i + 1) for i in range(n)])


def test_section_agent_returns_list_of_detailed_comments():
    client = _make_client()
    client.complete.return_value = _make_section_comments(2)

    agent = SectionAgent(client)
    result = agent.run(_make_section(), "Test Paper")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(c, DetailedComment) for c in result)


def test_section_agent_uses_text_prompt():
    """Always uses text-only system prompt and section_user."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    section = _make_section()
    agent = SectionAgent(client)
    agent.run(section, "My Paper")

    call_args = client.complete.call_args
    messages = call_args[0][0]

    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1
    # Text-only: content is a string, not a list
    assert isinstance(user_msgs[0]["content"], str)


def test_section_agent_min_one_comment():
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    agent = SectionAgent(client)
    result = agent.run(_make_section(), "Paper Title")

    assert len(result) == 1
    assert isinstance(result[0], DetailedComment)


def test_section_agent_max_five_comments():
    client = _make_client()
    client.complete.return_value = _make_section_comments(5)

    agent = SectionAgent(client)
    result = agent.run(_make_section(), "Paper Title")

    assert len(result) == 5
    assert all(isinstance(c, DetailedComment) for c in result)


def test_section_agent_truncates_long_text():
    """Sections longer than MAX_SECTION_CHARS are truncated."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    long_text = "A" * 600_000  # exceeds 500K limit
    section = _make_section(text=long_text)
    agent = SectionAgent(client)
    agent.run(section, "Paper Title")

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_content = messages[1]["content"]
    assert "[...truncated]" in user_content


def test_section_agent_passes_focus_to_prompt():
    """Different focus values select different system prompts."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    agent = SectionAgent(client)
    agent.run(_make_section(), "Paper", focus="proof")

    call_args = client.complete.call_args
    messages = call_args[0][0]
    system_msg = messages[0]["content"]
    # Proof system prompt mentions "theorem" or "proof checker"
    assert "proof" in system_msg.lower() or "theorem" in system_msg.lower()


def test_section_agent_prompt_caching():
    """With supports_prompt_caching=True, system content is a list with cache_control."""
    client = _make_client()
    client.supports_prompt_caching = True
    client.complete.return_value = _make_section_comments(1)

    agent = SectionAgent(client)
    agent.run(_make_section(), "Test Paper")

    messages = client.complete.call_args[0][0]
    system_msg = [m for m in messages if m["role"] == "system"][0]

    # System content must be a list with one text block bearing cache_control
    assert isinstance(system_msg["content"], list)
    assert len(system_msg["content"]) == 1
    block = system_msg["content"][0]
    assert block["type"] == "text"
    assert block["cache_control"] == {"type": "ephemeral"}

    # User message is still a plain string
    user_msg = [m for m in messages if m["role"] == "user"][0]
    assert isinstance(user_msg["content"], str)
