"""Tests for agents/cross_section.py — CrossSectionAgent."""

from unittest.mock import MagicMock

from coarse.agents.cross_section import CrossSectionAgent, _CrossSectionComments
from coarse.llm import LLMClient
from coarse.prompts import CROSS_SECTION_SYSTEM
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
    title: str = "Results",
    text: str = "Theorem 1 establishes that the estimator is consistent.",
    section_type: SectionType = SectionType.RESULTS,
) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=title,
        text=text,
        section_type=section_type,
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Gap {number}",
        quote="Theorem 1 establishes that the estimator is consistent.",
        feedback=f"The discussion overclaims relative to what Theorem {number} proves.",
    )


def _make_cross_section_comments(n: int) -> _CrossSectionComments:
    return _CrossSectionComments(comments=[_make_comment(i + 1) for i in range(n)])


def test_cross_section_agent_returns_comments():
    """Mock client.complete; verify run returns list[DetailedComment]."""
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(2)

    results_sec = _make_section(number=3, title="Main Results")
    discussion_sec = _make_section(
        number=5,
        title="Discussion",
        text="Our results show that the estimator works in general.",
        section_type=SectionType.DISCUSSION,
    )

    agent = CrossSectionAgent(client)
    result = agent.run("Test Paper", results_sec, discussion_sec)

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(c, DetailedComment) for c in result)


def test_cross_section_agent_empty_result():
    """Agent can return 0 comments when discussion matches results."""
    client = _make_client()
    client.complete.return_value = _CrossSectionComments(comments=[])

    agent = CrossSectionAgent(client)
    result = agent.run(
        "Test Paper",
        _make_section(),
        _make_section(number=4, title="Discussion", section_type=SectionType.DISCUSSION),
    )

    assert result == []


def test_cross_section_agent_uses_temperature_03():
    """client.complete is called with temperature=0.3."""
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(1)

    agent = CrossSectionAgent(client)
    agent.run(
        "Test Paper",
        _make_section(),
        _make_section(number=4, title="Discussion", section_type=SectionType.DISCUSSION),
    )

    _, kwargs = client.complete.call_args
    assert kwargs.get("temperature") == 0.3


def test_cross_section_agent_truncates_long_sections():
    """Sections longer than MAX_CONTEXT_CHARS are truncated before sending to LLM."""
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(1)

    long_text = "A" * 600_000  # exceeds 500K limit
    results_sec = _make_section(text=long_text)
    discussion_sec = _make_section(
        number=4,
        title="Discussion",
        text=long_text,
        section_type=SectionType.DISCUSSION,
    )

    agent = CrossSectionAgent(client)
    agent.run("Test Paper", results_sec, discussion_sec)

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_content = [m for m in messages if m["role"] == "user"][0]["content"]
    assert "[...truncated]" in user_content


def test_cross_section_agent_uses_correct_system_prompt():
    """System message content equals CROSS_SECTION_SYSTEM from prompts.py."""
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(1)

    agent = CrossSectionAgent(client)
    agent.run(
        "Test Paper",
        _make_section(),
        _make_section(number=4, title="Discussion", section_type=SectionType.DISCUSSION),
    )

    call_args = client.complete.call_args
    messages = call_args[0][0]
    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == CROSS_SECTION_SYSTEM


def test_cross_section_agent_passes_correct_response_model():
    """client.complete is called with _CrossSectionComments as response_model."""
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(1)

    agent = CrossSectionAgent(client)
    agent.run(
        "Test Paper",
        _make_section(),
        _make_section(number=4, title="Discussion", section_type=SectionType.DISCUSSION),
    )

    client.complete.assert_called_once()
    response_model = client.complete.call_args[0][1]
    assert response_model is _CrossSectionComments


def test_cross_section_agent_user_message_includes_both_sections():
    """User message contains text from both the results and discussion sections."""
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(1)

    results_sec = _make_section(
        number=3,
        title="Main Results",
        text="Theorem 1 proves consistency under regularity.",
    )
    discussion_sec = _make_section(
        number=5,
        title="Implications",
        text="Our framework has broad policy implications.",
        section_type=SectionType.DISCUSSION,
    )

    agent = CrossSectionAgent(client)
    agent.run("Test Paper", results_sec, discussion_sec)

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_content = [m for m in messages if m["role"] == "user"][0]["content"]
    assert "Theorem 1 proves consistency under regularity." in user_content
    assert "Our framework has broad policy implications." in user_content


def test_cross_section_agent_author_notes_prepend_to_user_message():
    client = _make_client()
    client.complete.return_value = _make_cross_section_comments(1)

    agent = CrossSectionAgent(client)
    agent.run(
        "Test Paper",
        _make_section(),
        _make_section(number=4, title="Discussion", section_type=SectionType.DISCUSSION),
        author_notes="focus on whether the policy claims overreach the theorem",
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    user_content = [m for m in messages if m["role"] == "user"][0]["content"]

    assert "focus on whether the policy claims overreach the theorem" not in system_content
    assert "<author_notes>" in user_content
    assert "focus on whether the policy claims overreach the theorem" in user_content


def test_cross_section_agent_prompt_caching():
    """With supports_prompt_caching=True, system content is a list with cache_control."""
    client = _make_client()
    client.supports_prompt_caching = True
    client.complete.return_value = _make_cross_section_comments(1)

    agent = CrossSectionAgent(client)
    agent.run(
        "Test Paper",
        _make_section(),
        _make_section(number=4, title="Discussion", section_type=SectionType.DISCUSSION),
    )

    messages = client.complete.call_args[0][0]
    system_msg = [m for m in messages if m["role"] == "system"][0]

    assert isinstance(system_msg["content"], list)
    assert len(system_msg["content"]) == 1
    block = system_msg["content"][0]
    assert block["type"] == "text"
    assert block["cache_control"] == {"type": "ephemeral"}
    assert CROSS_SECTION_SYSTEM in block["text"]


def test_cross_section_agent_manuscript_system_prompt_unchanged():
    """Manuscript path is byte-identical to CROSS_SECTION_SYSTEM."""
    client = _make_client()
    client.complete.return_value = _CrossSectionComments(comments=[])
    agent = CrossSectionAgent(client)

    agent.run(
        "Title",
        _make_section(),
        _make_section(2, "Discussion", "We interpret the result broadly.", SectionType.DISCUSSION),
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content == CROSS_SECTION_SYSTEM


def test_cross_section_agent_outline_gets_form_notice():
    """If the pipeline ever fires cross_section on a non-manuscript (unlikely
    due to the math_content gate, but possible on partial drafts with real
    results prose and stubbed discussion), the form notice must be appended
    so the 'is the discussion supported by formal results' frame relaxes."""
    client = _make_client()
    client.complete.return_value = _CrossSectionComments(comments=[])
    agent = CrossSectionAgent(client)

    agent.run(
        "Title",
        _make_section(),
        _make_section(2, "Discussion", "We interpret the result.", SectionType.DISCUSSION),
        document_form="draft",
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content.startswith(CROSS_SECTION_SYSTEM)
    assert "DOCUMENT FORM: PARTIAL DRAFT" in system_content
