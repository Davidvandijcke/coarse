"""Tests for coarse.agent.refutation.

Driven by a role-aware fake client, so these make no provider calls.

The behaviour that matters is asymmetric between the two halves of a review. A
detailed comment is anchored and is either reproduced or dropped. A macro issue
carries no anchor and bundles several points, so the common outcome is that some
hold and some do not: dropping the whole issue would discard the good points,
and keeping it whole would ship the bad one. These tests pin the narrowing path
and the guard against emptying the overall feedback entirely.
"""

from __future__ import annotations

import json

import pytest

from coarse.agent.refutation import (
    NO_ISSUES_SURVIVED,
    refute_comments,
    refute_issues,
    refute_review,
)
from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    SectionInfo,
    SectionType,
)

QUOTE_A = "The displayed gradient has the opposite sign from the derivative."
QUOTE_B = "The curvature bound is half the exact curvature under these definitions."
BODY = f"{QUOTE_A} {QUOTE_B} Padding to make the section substantial. " * 12

NARROWED = "Only the first of the three points stands: the gradient sign is reversed."


def _structure() -> PaperStructure:
    return PaperStructure(
        title="A Paper",
        domain="statistics",
        taxonomy="academic/research_paper",
        abstract="An abstract about stable selection.",
        sections=[
            SectionInfo(
                number="A.10",
                title="Proof of Proposition 2",
                text=BODY,
                section_type=SectionType.OTHER,
                math_content=True,
            )
        ],
    )


def _paper() -> str:
    return f"# A Paper\n\n# A.10\n\n{BODY}\n"


def _submit(payload: dict, call_id: str = "s1") -> dict:
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {"name": "submit", "arguments": json.dumps(payload)},
            }
        ],
    }


def _comment(number: int, title: str, quote: str) -> DetailedComment:
    return DetailedComment(
        number=number, title=title, quote=quote, feedback=f"{title}: this step fails."
    )


def _issue(title: str) -> OverviewIssue:
    return OverviewIssue(title=title, body=f"{title}. This concern makes three points.")


class FakeClient:
    """Answers by role, keyed on the system prompt.

    ``issue_verdicts`` maps an issue title to the verdict to return for it.
    """

    def __init__(
        self,
        *,
        comment_verdicts: dict[str, str] | None = None,
        issue_verdicts: dict[str, str] | None = None,
        rewritten: str = NARROWED,
    ) -> None:
        self.comment_verdicts = comment_verdicts or {}
        self.issue_verdicts = issue_verdicts or {}
        self.rewritten = rewritten
        self.issue_tasks: list[str] = []
        self.model = "fake/model"
        self.supports_prompt_caching = False
        self._cost = 0.0

    @property
    def cost_usd(self) -> float:
        return self._cost

    def complete_with_tools(self, messages, tools, **_kwargs) -> dict:
        self._cost += 0.01
        system = str(messages[0].get("content", ""))
        task = str(messages[1].get("content", "")) if len(messages) > 1 else ""

        if "macro-level concern" in system:
            self.issue_tasks.append(task)
            verdict = next(
                (v for title, v in self.issue_verdicts.items() if title in task), "supported"
            )
            return _submit(
                {
                    "issue_index": 0,
                    "verdict": verdict,
                    "rewritten_body": self.rewritten if verdict == "partly_supported" else "",
                    "dropped_points": (
                        ["point two is answered in Section 6"]
                        if verdict == "partly_supported"
                        else []
                    ),
                    "reasoning": "Checked each point against the paper.",
                }
            )
        if "check a single criticism" in system:
            verdict = next(
                (v for title, v in self.comment_verdicts.items() if title in task), "confirmed"
            )
            return _submit(
                {
                    "finding_id": "x",
                    "verdict": verdict,
                    "reasoning": "Checked against the paper.",
                    "severity_after_review": "major",
                }
            )
        return {"role": "assistant", "content": "unrecognized role"}


# -- issues ---------------------------------------------------------------


def test_a_supported_issue_is_kept_unchanged(tmp_path):
    issue = _issue("Shared variance estimate")
    kept, verdicts, records = refute_issues(
        [issue],
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Shared variance estimate": "supported"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "w1"),
    )
    assert kept == [issue]
    assert [v.verdict for v in verdicts] == ["supported"]
    assert len(records) == 1


def test_a_refuted_issue_is_dropped(tmp_path):
    # Two issues, so dropping is observed on its own rather than through the
    # all-refuted guard that fires when nothing at all survives.
    kept, _v, _r = refute_issues(
        [_issue("Stands up"), _issue("Answered in Section 6")],
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Answered in Section 6": "refuted"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "w2"),
    )
    assert [i.title for i in kept] == ["Stands up"]


def test_a_partly_supported_issue_is_narrowed_not_dropped(tmp_path):
    """The path that distinguishes an issue from a comment.

    An issue making three points, one of which is answered elsewhere, must
    reach the author with the two that hold rather than not at all.
    """
    kept, verdicts, _r = refute_issues(
        [_issue("Error budget accounting")],
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Error budget accounting": "partly_supported"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "w3"),
    )
    assert len(kept) == 1
    assert kept[0].title == "Error budget accounting", "the title must survive narrowing"
    assert kept[0].body == NARROWED
    assert verdicts[0].dropped_points == ["point two is answered in Section 6"]


def test_a_narrowing_with_no_replacement_text_keeps_the_original(tmp_path):
    """Keeping the original is the safe reading: the reviewer called it partly
    right, so dropping it would lose a concern it endorsed."""
    original = _issue("Error budget accounting")
    kept, _v, _r = refute_issues(
        [original],
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Error budget accounting": "partly_supported"}, rewritten="   "),
        max_parallel=1,
        workspace_root=str(tmp_path / "w4"),
    )
    assert kept == [original]


def test_an_inconclusive_issue_is_kept(tmp_path):
    original = _issue("Hard to settle")
    kept, _v, _r = refute_issues(
        [original],
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Hard to settle": "inconclusive"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "w5"),
    )
    assert kept == [original], "uncertainty must not be resolved into a deletion"


def test_an_issue_whose_check_could_not_run_is_kept(tmp_path):
    class Broken(FakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            if "macro-level concern" in str(messages[0].get("content", "")):
                raise RuntimeError("provider down")
            return super().complete_with_tools(messages, tools, **kwargs)

    original = _issue("Shared variance estimate")
    kept, verdicts, _r = refute_issues(
        [original],
        _paper(),
        _structure(),
        Broken(),
        max_parallel=1,
        workspace_root=str(tmp_path / "w6"),
    )
    assert kept == [original]
    assert verdicts == []


def test_refuting_every_issue_substitutes_an_explicit_notice(tmp_path):
    """``OverviewFeedback`` requires an issue, and reinstating the least-bad
    refuted one would put back a claim the paper contradicts."""
    kept, _v, _r = refute_issues(
        [_issue("Wrong one"), _issue("Also wrong")],
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Wrong one": "refuted", "Also wrong": "refuted"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "w7"),
    )
    assert kept == [NO_ISSUES_SURVIVED]
    assert "did not establish one" in kept[0].body


def test_issue_refuter_gets_no_quote_and_must_search(tmp_path):
    """An issue has no anchor; the prompt must not pretend otherwise."""
    client = FakeClient(issue_verdicts={"Shared variance estimate": "supported"})
    refute_issues(
        [_issue("Shared variance estimate")],
        _paper(),
        _structure(),
        client,
        max_parallel=1,
        workspace_root=str(tmp_path / "w8"),
    )
    task = client.issue_tasks[0]
    assert "Shared variance estimate" in task
    assert "QUOTE" not in task
    assert "Break it into its separate claims" in task


def test_refute_issues_on_an_empty_list_is_a_noop(tmp_path):
    assert refute_issues([], _paper(), _structure(), FakeClient()) == ([], [], [])


def test_issues_are_refuted_in_order_independent_of_completion(tmp_path):
    """Verdicts come back out of order under parallelism, so the kept list
    must be rebuilt by index rather than by arrival."""
    issues = [_issue(f"Concern {i}") for i in range(1, 5)]
    kept, _v, _r = refute_issues(
        issues,
        _paper(),
        _structure(),
        FakeClient(issue_verdicts={"Concern 2": "refuted"}),
        max_parallel=4,
        workspace_root=str(tmp_path / "w9"),
    )
    assert [i.title for i in kept] == ["Concern 1", "Concern 3", "Concern 4"]


# -- both halves together -------------------------------------------------


def test_refute_review_checks_comments_and_issues(tmp_path):
    overview = OverviewFeedback(
        issues=[_issue("Good concern"), _issue("Bad concern")],
        assessment="An assessment.",
    )
    comments = [_comment(1, "Sign error", QUOTE_A), _comment(2, "Curvature", QUOTE_B)]
    client = FakeClient(
        comment_verdicts={"Curvature": "refuted"},
        issue_verdicts={"Bad concern": "refuted"},
    )
    new_overview, kept_comments, records = refute_review(
        overview, comments, _paper(), _structure(), client, max_parallel=1
    )
    assert [i.title for i in new_overview.issues] == ["Good concern"]
    assert [c.title for c in kept_comments] == ["Sign error"]
    assert new_overview.assessment == "An assessment.", "untouched fields must survive"
    assert len(records) == 4


@pytest.mark.parametrize("broken_half", ["comments", "issues"])
def test_refute_review_fails_each_half_independently(tmp_path, broken_half):
    """A failure in one half must leave the other verified, not lose both."""

    class HalfBroken(FakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            system = str(messages[0].get("content", ""))
            if broken_half == "issues" and "macro-level concern" in system:
                raise RuntimeError("down")
            if broken_half == "comments" and "check a single criticism" in system:
                raise RuntimeError("down")
            return super().complete_with_tools(messages, tools, **kwargs)

    overview = OverviewFeedback(issues=[_issue("Good"), _issue("Bad")])
    comments = [_comment(1, "Sign error", QUOTE_A), _comment(2, "Curvature", QUOTE_B)]
    client = HalfBroken(
        comment_verdicts={"Curvature": "refuted"}, issue_verdicts={"Bad": "refuted"}
    )
    new_overview, kept_comments, _records = refute_review(
        overview, comments, _paper(), _structure(), client, max_parallel=1
    )

    if broken_half == "issues":
        assert len(new_overview.issues) == 2, "unverified issues are kept"
        assert [c.title for c in kept_comments] == ["Sign error"], "comments still verified"
    else:
        assert [i.title for i in new_overview.issues] == ["Good"], "issues still verified"
        assert len(kept_comments) == 2, "unverified comments are kept"


def test_refute_comments_still_drops_what_is_not_reproduced(tmp_path):
    kept, _v, _r = refute_comments(
        [_comment(1, "Sign error", QUOTE_A), _comment(2, "Curvature", QUOTE_B)],
        _paper(),
        _structure(),
        FakeClient(comment_verdicts={"Curvature": "refuted"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "w10"),
    )
    assert [c.title for c in kept] == ["Sign error"]
