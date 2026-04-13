"""Tests for agents/completeness.py — CompletenessAgent."""

from unittest.mock import MagicMock

from coarse.agents.completeness import CompletenessAgent, _CompletenessResult
from coarse.llm import LLMClient
from coarse.prompts import COMPLETENESS_SYSTEM
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
                claims=["Claim 1"],
            ),
            SectionInfo(
                number=2,
                title="Results",
                text="Results text here.",
                section_type=SectionType.RESULTS,
            ),
        ],
    )


def _make_overview() -> OverviewFeedback:
    return OverviewFeedback(
        issues=[OverviewIssue(title=f"Issue {i}", body=f"Body of issue {i}.") for i in range(1, 5)]
    )


def _make_completeness_result(n: int) -> _CompletenessResult:
    return _CompletenessResult(
        issues=[
            OverviewIssue(title=f"Gap {i}", body=f"Missing content {i}.") for i in range(1, n + 1)
        ]
    )


def test_completeness_agent_returns_issues():
    """Mock LLMClient.complete; assert run() returns list of OverviewIssue."""
    client = _make_client()
    client.complete.return_value = _make_completeness_result(2)

    agent = CompletenessAgent(client)
    result = agent.run(_make_structure(), _make_overview())

    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(i, OverviewIssue) for i in result)


def test_completeness_agent_empty_result():
    """Agent can return 0 issues (_CompletenessResult allows empty list)."""
    client = _make_client()
    client.complete.return_value = _CompletenessResult(issues=[])

    agent = CompletenessAgent(client)
    result = agent.run(_make_structure(), _make_overview())

    assert result == []


def test_completeness_result_allows_empty_issues():
    """_CompletenessResult should validate with an empty issues list (unlike OverviewFeedback)."""
    result = _CompletenessResult(issues=[])
    assert result.issues == []


def test_completeness_agent_passes_correct_response_model():
    """client.complete is called with _CompletenessResult as response_model."""
    client = _make_client()
    client.complete.return_value = _make_completeness_result(1)

    agent = CompletenessAgent(client)
    agent.run(_make_structure(), _make_overview())

    client.complete.assert_called_once()
    call_args = client.complete.call_args
    response_model = call_args[0][1]
    assert response_model is _CompletenessResult


def test_completeness_agent_uses_temperature_05():
    """client.complete is called with temperature=0.5."""
    client = _make_client()
    client.complete.return_value = _make_completeness_result(1)

    agent = CompletenessAgent(client)
    agent.run(_make_structure(), _make_overview())

    _, kwargs = client.complete.call_args
    assert kwargs.get("temperature") == 0.5


def test_completeness_agent_uses_correct_system_prompt():
    """System message content equals COMPLETENESS_SYSTEM from prompts.py."""
    client = _make_client()
    client.complete.return_value = _make_completeness_result(1)

    agent = CompletenessAgent(client)
    agent.run(_make_structure(), _make_overview())

    call_args = client.complete.call_args
    messages = call_args[0][0]
    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == COMPLETENESS_SYSTEM


def test_completeness_agent_user_message_includes_title_and_abstract():
    """User message contains the paper title and abstract."""
    client = _make_client()
    client.complete.return_value = _make_completeness_result(1)

    structure = _make_structure()
    agent = CompletenessAgent(client)
    agent.run(structure, _make_overview())

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1
    user_content = user_msgs[0]["content"]
    assert structure.title in user_content
    assert structure.abstract in user_content


def test_completeness_agent_user_message_includes_overview_issues():
    """User message contains the overview issue titles (so agent avoids repeating them)."""
    client = _make_client()
    client.complete.return_value = _make_completeness_result(1)

    overview = _make_overview()
    agent = CompletenessAgent(client)
    agent.run(_make_structure(), overview)

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_content = [m for m in messages if m["role"] == "user"][0]["content"]

    for issue in overview.issues:
        assert issue.title in user_content


def test_completeness_agent_author_notes_prepend_to_user_message():
    client = _make_client()
    client.complete.return_value = _make_completeness_result(1)

    agent = CompletenessAgent(client)
    agent.run(
        _make_structure(),
        _make_overview(),
        author_notes="the discussion section is still a placeholder",
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    user_content = [m for m in messages if m["role"] == "user"][0]["content"]

    assert "the discussion section is still a placeholder" not in system_content
    assert "<author_notes>" in user_content
    assert "the discussion section is still a placeholder" in user_content


def test_completeness_agent_prompt_caching():
    """With supports_prompt_caching=True, system content is a list with cache_control."""
    client = _make_client()
    client.supports_prompt_caching = True
    client.complete.return_value = _make_completeness_result(1)

    agent = CompletenessAgent(client)
    agent.run(_make_structure(), _make_overview())

    messages = client.complete.call_args[0][0]
    system_msg = [m for m in messages if m["role"] == "system"][0]

    assert isinstance(system_msg["content"], list)
    assert len(system_msg["content"]) == 1
    block = system_msg["content"][0]
    assert block["type"] == "text"
    assert block["cache_control"] == {"type": "ephemeral"}
    assert COMPLETENESS_SYSTEM in block["text"]


# ---------------------------------------------------------------------------
# document_form branching
# ---------------------------------------------------------------------------


def _structure_with_form(form: str) -> PaperStructure:
    return PaperStructure(
        title="t",
        domain="x",
        taxonomy="y",
        abstract="a",
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text="intro",
                section_type=SectionType.INTRODUCTION,
            ),
        ],
        document_form=form,
    )


def _empty_overview() -> OverviewFeedback:
    return OverviewFeedback(
        issues=[OverviewIssue(title=f"Issue {i}", body=f"body {i}") for i in range(5)]
    )


def test_completeness_skips_outline_without_calling_llm():
    """Completeness agent must short-circuit to [] for document_form='outline'
    — flagging missing content on a pure outline generates the exact
    defensive noise this whole feature is trying to eliminate. The LLM client
    must not be touched."""
    client = _make_client()
    agent = CompletenessAgent(client)

    result = agent.run(_structure_with_form("outline"), _empty_overview())

    assert result == []
    assert client.complete.call_count == 0


def test_completeness_skips_notes_without_calling_llm():
    """Working notes are not peer-review targets — same early-return."""
    client = _make_client()
    agent = CompletenessAgent(client)
    result = agent.run(_structure_with_form("notes"), _empty_overview())
    assert result == []
    assert client.complete.call_count == 0


def test_completeness_skips_other_without_calling_llm():
    """'other' docs fall through the same escape hatch — no peer review."""
    client = _make_client()
    agent = CompletenessAgent(client)
    result = agent.run(_structure_with_form("other"), _empty_overview())
    assert result == []
    assert client.complete.call_count == 0


def test_completeness_runs_on_manuscript_with_unchanged_prompt():
    """For manuscript, the system prompt sent is byte-identical to
    COMPLETENESS_SYSTEM (no notice suffix)."""
    client = _make_client()
    client.complete.return_value = _CompletenessResult(issues=[])
    agent = CompletenessAgent(client)

    agent.run(_structure_with_form("manuscript"), _empty_overview())

    assert client.complete.call_count == 1
    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content == COMPLETENESS_SYSTEM


def test_completeness_runs_on_draft_with_form_notice():
    """Partial drafts DO run completeness but with the draft-specific notice
    appended. The agent can still flag 'you haven't addressed X yet' — it
    just shouldn't list every stubbed section as its own issue."""
    client = _make_client()
    client.complete.return_value = _CompletenessResult(issues=[])
    agent = CompletenessAgent(client)

    agent.run(_structure_with_form("draft"), _empty_overview())

    assert client.complete.call_count == 1
    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content.startswith(COMPLETENESS_SYSTEM)
    assert "DOCUMENT FORM: PARTIAL DRAFT" in system_content


def test_completeness_runs_on_proposal_with_form_notice():
    """Research proposals run completeness too — feasibility / rationale
    gaps are still worth flagging. The notice tells the reviewer not to
    demand results."""
    client = _make_client()
    client.complete.return_value = _CompletenessResult(issues=[])
    agent = CompletenessAgent(client)

    agent.run(_structure_with_form("proposal"), _empty_overview())

    assert client.complete.call_count == 1
    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert "DOCUMENT FORM: RESEARCH PROPOSAL" in system_content


def test_completeness_runs_on_report_with_form_notice():
    """Technical reports (form='report') should NOT be in the skip set —
    gaps in the reasoning or evidence of a report are still worth flagging.
    The notice block tells the reviewer to judge by report-genre standards,
    not peer-review standards.
    """
    client = _make_client()
    client.complete.return_value = _CompletenessResult(issues=[])
    agent = CompletenessAgent(client)

    agent.run(_structure_with_form("report"), _empty_overview())

    assert client.complete.call_count == 1
    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert "DOCUMENT FORM: TECHNICAL REPORT" in system_content
