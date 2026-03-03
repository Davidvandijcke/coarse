"""Tests for agents/section.py — SectionAgent."""
from unittest.mock import MagicMock

from coarse.agents.section import SectionAgent, _SectionComments
from coarse.llm import LLMClient
from coarse.prompts import SECTION_SYSTEM, section_user
from coarse.types import DetailedComment, SectionInfo, SectionType


def _make_client() -> LLMClient:
    return MagicMock(spec=LLMClient)


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
    """Mock LLMClient.complete to return _SectionComments with 2 comments; assert run() returns list[DetailedComment] of length 2."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(2)

    agent = SectionAgent(client)
    result = agent.run(_make_section(), "Test Paper")

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(c, DetailedComment) for c in result)
    assert result[0].number == 1
    assert result[1].number == 2


def test_section_agent_passes_correct_messages():
    """Capture messages kwarg passed to client.complete; verify system content equals SECTION_SYSTEM and user content contains section title and text."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    section = _make_section()
    agent = SectionAgent(client)
    agent.run(section, "My Paper Title")

    client.complete.assert_called_once()
    call_args = client.complete.call_args
    messages = call_args[0][0]

    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == SECTION_SYSTEM

    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1
    user_content = user_msgs[0]["content"]
    assert section.title in user_content
    assert section.text in user_content


def test_section_agent_min_one_comment():
    """Mock returns _SectionComments with 1 comment; assert run() returns list of length 1."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    agent = SectionAgent(client)
    result = agent.run(_make_section(), "Paper Title")

    assert len(result) == 1
    assert isinstance(result[0], DetailedComment)


def test_section_agent_max_five_comments():
    """Mock returns _SectionComments with 5 comments; assert run() returns list of length 5."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(5)

    agent = SectionAgent(client)
    result = agent.run(_make_section(), "Paper Title")

    assert len(result) == 5
    assert all(isinstance(c, DetailedComment) for c in result)


def test_section_agent_uses_section_user_prompt():
    """Verify that section_user(paper_title, section) output appears in the user message."""
    client = _make_client()
    client.complete.return_value = _make_section_comments(1)

    paper_title = "Economics of Education"
    section = _make_section(
        title="Empirical Strategy",
        text="We use a regression discontinuity design.",
        claims=["RD identifies local average treatment effect"],
    )

    agent = SectionAgent(client)
    agent.run(section, paper_title)

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    user_content = user_msgs[0]["content"]

    expected_user = section_user(paper_title, section)
    assert user_content == expected_user
    assert paper_title in user_content
    assert section.title in user_content
    assert section.text in user_content
