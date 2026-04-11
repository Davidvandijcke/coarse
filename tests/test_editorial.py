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


# ---------------------------------------------------------------------------
# document_form branching
# ---------------------------------------------------------------------------


def test_editorial_agent_manuscript_system_prompt_unchanged():
    """For document_form='manuscript' (default), system prompt is byte-identical
    to EDITORIAL_SYSTEM — the manuscript path must not regress."""
    from coarse.prompts import EDITORIAL_SYSTEM

    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])
    agent = EditorialAgent(client)

    agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1)],
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content == EDITORIAL_SYSTEM


def test_editorial_agent_outline_gets_form_notice():
    from coarse.prompts import EDITORIAL_SYSTEM

    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])
    agent = EditorialAgent(client)

    agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1)],
        document_form="outline",
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert system_content.startswith(EDITORIAL_SYSTEM)
    assert "DOCUMENT FORM: OUTLINE" in system_content


def test_editorial_agent_form_notice_applies_even_with_comment_target():
    """When comment_target is set, editorial_system(target) is used as the
    base — but the form notice must still be appended on top."""
    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])
    agent = EditorialAgent(client)

    agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1)],
        comment_target=10,
        document_form="draft",
    )

    messages = client.complete.call_args[0][0]
    system_content = [m for m in messages if m["role"] == "system"][0]["content"]
    assert "DOCUMENT FORM: PARTIAL DRAFT" in system_content


# ---------------------------------------------------------------------------
# Author steering notes (#54)
# ---------------------------------------------------------------------------


def test_editorial_no_author_notes_user_message_unchanged():
    """None / omitted / whitespace-only author_notes must produce byte-identical
    user content to the pre-feature behavior."""
    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])

    agent = EditorialAgent(client)
    agent.run(paper_text="Paper body.", overview=_overview(), comments=[_comment(1)])
    user_plain = client.complete.call_args[0][0][1]["content"]

    client.complete.reset_mock()
    agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1)],
        author_notes=None,
    )
    user_none = client.complete.call_args[0][0][1]["content"]

    client.complete.reset_mock()
    agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1)],
        author_notes="   ",
    )
    user_empty = client.complete.call_args[0][0][1]["content"]

    assert user_plain == user_none == user_empty


def test_editorial_author_notes_prepend_to_user_message():
    client = MagicMock()
    client.supports_prompt_caching = False
    client.complete.return_value = _EditorialComments(comments=[_comment(1)])

    agent = EditorialAgent(client)
    agent.run(
        paper_text="Paper body.",
        overview=_overview(),
        comments=[_comment(1), _comment(2)],
        author_notes="keep comments that address the identification strategy",
    )

    messages = client.complete.call_args[0][0]
    system_content = messages[0]["content"]
    user_content = messages[1]["content"]

    # Notes TEXT must not leak into system (cached prompt). The fence-tag
    # name "author_notes" does appear there (boundary notice lists it) so
    # we check for the content instead.
    assert "keep comments that address the identification strategy" not in system_content
    assert "<author_notes>" in user_content
    assert "keep comments that address the identification strategy" in user_content
