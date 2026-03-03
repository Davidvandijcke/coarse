"""Tests for agents/crossref.py — CrossrefAgent."""
from unittest.mock import MagicMock

from coarse.agents.crossref import CrossrefAgent, _ConsolidatedComments
from coarse.llm import LLMClient
from coarse.prompts import CROSSREF_SYSTEM
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, PageContent, PaperText


def _make_client() -> LLMClient:
    return MagicMock(spec=LLMClient)


def _make_paper_text(markdown: str = "Full paper text here.") -> PaperText:
    return PaperText(
        full_markdown=markdown,
        pages=[PageContent(page_num=1, text=markdown)],
        token_estimate=100,
    )


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
        quote="Full paper text here.",
        feedback=f"Feedback for comment {number}.",
    )


def _make_consolidated(numbers: list[int]) -> _ConsolidatedComments:
    return _ConsolidatedComments(
        comments=[_make_comment(n) for n in numbers]
    )


def test_crossref_returns_detailed_comments():
    """Mock LLMClient.complete to return _ConsolidatedComments with 3 comments; verify run returns list[DetailedComment] of length 3."""
    client = _make_client()
    client.complete.return_value = _make_consolidated([1, 2, 3])

    agent = CrossrefAgent(client)
    result = agent.run(_make_paper_text(), _make_overview(), [_make_comment(1)])

    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(c, DetailedComment) for c in result)


def test_crossref_comments_renumbered_sequentially():
    """Given comments with non-sequential numbers, verify the returned list has sequential numbers."""
    client = _make_client()
    client.complete.return_value = _make_consolidated([1, 2, 3])

    input_comments = [_make_comment(2), _make_comment(5), _make_comment(7)]
    agent = CrossrefAgent(client)
    result = agent.run(_make_paper_text(), _make_overview(), input_comments)

    assert [c.number for c in result] == [1, 2, 3]


def test_crossref_passes_full_paper_text():
    """Capture messages passed to LLMClient.complete and assert paper_text.full_markdown appears in user message."""
    client = _make_client()
    client.complete.return_value = _make_consolidated([1])

    paper_markdown = "This is the unique paper content for verification."
    agent = CrossrefAgent(client)
    agent.run(_make_paper_text(paper_markdown), _make_overview(), [_make_comment(1)])

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1
    assert paper_markdown in user_msgs[0]["content"]


def test_crossref_passes_overview_issues():
    """Assert that overview issue titles appear in the user message content sent to the LLM."""
    client = _make_client()
    client.complete.return_value = _make_consolidated([1])

    overview = _make_overview()
    agent = CrossrefAgent(client)
    agent.run(_make_paper_text(), overview, [_make_comment(1)])

    call_args = client.complete.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    user_content = user_msgs[0]["content"]

    for issue in overview.issues:
        assert issue.title in user_content


def test_crossref_empty_comments_list():
    """Pass an empty comments list; verify the agent does not raise and returns an empty list."""
    client = _make_client()
    client.complete.return_value = _ConsolidatedComments(comments=[])

    agent = CrossrefAgent(client)
    result = agent.run(_make_paper_text(), _make_overview(), [])

    assert result == []


def test_crossref_uses_crossref_system_prompt():
    """Assert that the system message content equals CROSSREF_SYSTEM from prompts.py."""
    client = _make_client()
    client.complete.return_value = _make_consolidated([1])

    agent = CrossrefAgent(client)
    agent.run(_make_paper_text(), _make_overview(), [_make_comment(1)])

    call_args = client.complete.call_args
    messages = call_args[0][0]
    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert system_msgs[0]["content"] == CROSSREF_SYSTEM
