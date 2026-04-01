"""Tests for agents/overview.py — OverviewAgent."""
from unittest.mock import MagicMock

from coarse.agents.overview import OverviewAgent, _build_sections_text
from coarse.llm import LLMClient
from coarse.prompts import OVERVIEW_SYSTEM
from coarse.types import (
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    SectionInfo,
    SectionType,
)


def _make_client() -> LLMClient:
    client = MagicMock(spec=LLMClient)
    client.supports_prompt_caching = False
    return client


def _make_structure() -> PaperStructure:
    return PaperStructure(
        title="Test Paper Title",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="This is the abstract of the test paper.",
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text="Introduction text here.",
                section_type=SectionType.INTRODUCTION,
                claims=["Claim 1", "Claim 2"],
                definitions=["Term A"],
            ),
            SectionInfo(
                number=2,
                title="Methodology",
                text="Methodology text here.",
                section_type=SectionType.METHODOLOGY,
                claims=["Claim 3"],
                definitions=[],
            ),
            SectionInfo(
                number=3,
                title="Results",
                text="Results text here.",
                section_type=SectionType.RESULTS,
                claims=[],
                definitions=[],
            ),
        ],
    )


def _make_feedback() -> OverviewFeedback:
    return OverviewFeedback(
        issues=[
            OverviewIssue(title=f"Issue {i}", body=f"Body of issue {i}.")
            for i in range(1, 6)
        ]
    )


def test_overview_agent_returns_overview_feedback():
    """Mock LLMClient.complete to return OverviewFeedback; assert run() returns it unchanged."""
    client = _make_client()
    expected = _make_feedback()
    client.complete.return_value = expected

    agent = OverviewAgent(client)
    result = agent.run(_make_structure())

    assert result is expected


def test_overview_agent_calls_complete_with_correct_model():
    """Verify client.complete is called once with OverviewFeedback as response_model and OVERVIEW_SYSTEM as system."""
    client = _make_client()
    client.complete.return_value = _make_feedback()

    agent = OverviewAgent(client)
    agent.run(_make_structure())

    client.complete.assert_called_once()
    call_args = client.complete.call_args
    messages = call_args[0][0]
    response_model = call_args[0][1]

    assert response_model is OverviewFeedback
    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == OVERVIEW_SYSTEM


def test_build_sections_text_includes_all_sections():
    """All section titles appear in the output string."""
    sections = [
        SectionInfo(
            number=1,
            title="Intro",
            text="...",
            section_type=SectionType.INTRODUCTION,
            claims=["Claim A", "Claim B"],
        ),
        SectionInfo(
            number=2,
            title="Methods",
            text="...",
            section_type=SectionType.METHODOLOGY,
            claims=["Claim C"],
        ),
        SectionInfo(
            number=3,
            title="Results",
            text="...",
            section_type=SectionType.RESULTS,
            claims=["Claim D", "Claim E"],
        ),
    ]
    result = _build_sections_text(sections)

    for sec in sections:
        assert sec.title in result


def test_build_sections_text_no_truncation():
    """Full text is preserved without truncation."""
    long_text = "A" * 15_000
    sections = [
        SectionInfo(
            number=1,
            title="Introduction",
            text=long_text,
            section_type=SectionType.INTRODUCTION,
        ),
    ]
    result = _build_sections_text(sections)
    assert long_text in result
    assert "[...truncated]" not in result


def test_build_sections_text_empty_text():
    """Sections with empty text should show (empty)."""
    sections = [
        SectionInfo(number=1, title="Empty", text="",
                    section_type=SectionType.OTHER),
    ]
    result = _build_sections_text(sections)
    assert "(empty)" in result


def test_overview_agent_passes_title_and_abstract():
    """User message contains the paper title and abstract from PaperStructure."""
    client = _make_client()
    client.complete.return_value = _make_feedback()

    structure = _make_structure()
    agent = OverviewAgent(client)
    agent.run(structure)

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1
    user_content = user_msgs[0]["content"]
    assert structure.title in user_content
    assert structure.abstract in user_content


def test_overview_agent_uses_temperature_03():
    """client.complete is called with temperature=0.3."""
    client = _make_client()
    client.complete.return_value = _make_feedback()

    agent = OverviewAgent(client)
    agent.run(_make_structure())

    _, kwargs = client.complete.call_args
    assert kwargs.get("temperature") == 0.3


def test_overview_agent_prompt_caching_layout():
    """With supports_prompt_caching=True, system content is a list with 2 blocks:
    first has cache_control and paper context, second has OVERVIEW_SYSTEM."""
    client = _make_client()
    client.supports_prompt_caching = True
    client.complete.return_value = _make_feedback()

    agent = OverviewAgent(client)
    agent.run(_make_structure())

    messages = client.complete.call_args[0][0]
    system_msg = [m for m in messages if m["role"] == "system"][0]

    # System content must be a list of 2 content blocks
    assert isinstance(system_msg["content"], list)
    assert len(system_msg["content"]) == 2

    # First block: paper context with cache_control
    first = system_msg["content"][0]
    assert first["type"] == "text"
    assert first["cache_control"] == {"type": "ephemeral"}
    # Paper context should contain title and abstract
    assert "Test Paper Title" in first["text"]
    assert "abstract of the test paper" in first["text"]

    # Second block: OVERVIEW_SYSTEM (no cache_control)
    second = system_msg["content"][1]
    assert second["type"] == "text"
    assert second["text"] == OVERVIEW_SYSTEM
    assert "cache_control" not in second


def test_overview_agent_prompt_caching_short_user_message():
    """With caching, user message is a short trigger (paper content is in system)."""
    client = _make_client()
    client.supports_prompt_caching = True
    client.complete.return_value = _make_feedback()

    structure = _make_structure()
    agent = OverviewAgent(client)
    agent.run(structure)

    messages = client.complete.call_args[0][0]
    user_msg = [m for m in messages if m["role"] == "user"][0]

    # User message should be short — no sections summary or abstract embedded
    assert isinstance(user_msg["content"], str)
    assert len(user_msg["content"]) < 300
    # Should not contain full section text
    assert "Methodology text here." not in user_msg["content"]
