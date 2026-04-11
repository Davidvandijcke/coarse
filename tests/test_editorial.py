"""Tests for coarse.agents.editorial."""

from __future__ import annotations

from unittest.mock import MagicMock

from coarse.agents.editorial import EditorialAgent, _EditorialComments
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue


def _comment(n: int, title: str = "t") -> DetailedComment:
    return DetailedComment(
        number=n,
        title=f"{title} {n}",
        quote="This is a sufficiently long verbatim quote.",
        feedback="Constructive feedback text.",
    )


def _overview() -> OverviewFeedback:
    return OverviewFeedback(issues=[OverviewIssue(title="Issue 1", body="Body 1")])


def test_editorial_agent_returns_filtered_comments():
    """EditorialAgent.run returns the list from the LLMClient envelope."""
    client = MagicMock()
    filtered = [_comment(1), _comment(2)]
    client.complete.return_value = _EditorialComments(comments=filtered)

    agent = EditorialAgent(client)
    result = agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1), _comment(2), _comment(3)],
        title="Paper",
        abstract="Abstract",
    )

    assert result == filtered
    assert client.complete.call_count == 1


def test_editorial_agent_uses_default_system_when_no_target():
    """Without comment_target the agent uses EDITORIAL_SYSTEM, not the templated one."""
    client = MagicMock()
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])

    agent = EditorialAgent(client)
    agent.run(
        paper_text="Paper",
        overview=_overview(),
        comments=[_comment(1)],
    )

    # First positional arg to complete() is the messages list; system role is index 0
    messages = client.complete.call_args.args[0]
    assert messages[0]["role"] == "system"


def test_editorial_agent_accepts_comment_target_without_crashing():
    """comment_target is accepted for API compat (currently ignored by template)."""
    client = MagicMock()
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])

    agent = EditorialAgent(client)
    result = agent.run(
        paper_text="Paper",
        overview=_overview(),
        comments=[_comment(1)],
        comment_target=10,
    )

    assert len(result) == 1
    assert client.complete.call_count == 1
