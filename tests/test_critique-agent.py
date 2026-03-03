"""Tests for agents/critique.py — CritiqueAgent."""
from unittest.mock import MagicMock

from coarse.agents.critique import CritiqueAgent, _RevisedComments
from coarse.llm import LLMClient
from coarse.prompts import CRITIQUE_SYSTEM, critique_user
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue


def _make_client() -> LLMClient:
    return MagicMock(spec=LLMClient)


def _make_overview() -> OverviewFeedback:
    return OverviewFeedback(
        issues=[
            OverviewIssue(title=f"Issue {i}", body=f"Body of issue {i}.")
            for i in range(1, 5)
        ]
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote=f"Verbatim quote for comment {number}.",
        feedback=f"Feedback for comment {number}.",
    )


def _make_revised(numbers: list[int]) -> _RevisedComments:
    return _RevisedComments(comments=[_make_comment(n) for n in numbers])


def test_critique_returns_list_of_detailed_comments():
    """Verify run() returns a list[DetailedComment] when called with valid overview and comments."""
    client = _make_client()
    client.complete.return_value = _make_revised([1, 2, 3])

    agent = CritiqueAgent(client)
    result = agent.run(_make_overview(), [_make_comment(1), _make_comment(2), _make_comment(3)])

    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(c, DetailedComment) for c in result)


def test_critique_renumbers_sequentially():
    """Verify returned comments are numbered 1..N with no gaps, regardless of input numbering."""
    client = _make_client()
    client.complete.return_value = _make_revised([1, 2, 3])

    input_comments = [_make_comment(3), _make_comment(7), _make_comment(15)]
    agent = CritiqueAgent(client)
    result = agent.run(_make_overview(), input_comments)

    assert [c.number for c in result] == [1, 2, 3]


def test_critique_drops_comments():
    """Mock LLM to return fewer comments than input; verify output length is smaller and no error occurs."""
    client = _make_client()
    client.complete.return_value = _make_revised([1, 2])

    input_comments = [_make_comment(i) for i in range(1, 6)]
    agent = CritiqueAgent(client)
    result = agent.run(_make_overview(), input_comments)

    assert len(result) == 2
    assert all(isinstance(c, DetailedComment) for c in result)


def test_critique_preserves_good_comments():
    """Mock LLM to return all input comments unchanged; verify content is preserved verbatim."""
    client = _make_client()
    input_comments = [_make_comment(i) for i in range(1, 4)]
    client.complete.return_value = _RevisedComments(comments=list(input_comments))

    agent = CritiqueAgent(client)
    result = agent.run(_make_overview(), input_comments)

    assert len(result) == len(input_comments)
    for original, returned in zip(input_comments, result):
        assert returned.title == original.title
        assert returned.quote == original.quote
        assert returned.feedback == original.feedback


def test_critique_empty_input():
    """Pass an empty comments list; verify agent returns empty list without error."""
    client = _make_client()
    client.complete.return_value = _RevisedComments(comments=[])

    agent = CritiqueAgent(client)
    result = agent.run(_make_overview(), [])

    assert result == []


def test_critique_uses_correct_prompts():
    """Spy on client.complete to confirm CRITIQUE_SYSTEM is passed as system role and critique_user output appears in user message."""
    client = _make_client()
    client.complete.return_value = _make_revised([1])

    overview = _make_overview()
    comments = [_make_comment(1)]
    agent = CritiqueAgent(client)
    agent.run(overview, comments)

    call_args = client.complete.call_args
    messages = call_args[0][0]

    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == CRITIQUE_SYSTEM

    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1
    expected_user = critique_user(overview, comments)
    assert user_msgs[0]["content"] == expected_user
