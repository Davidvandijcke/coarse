"""Tests for coarse.agent.refutation.

Driven by a role-aware fake client, so these make no provider calls.

The behaviour that matters is that the gate only ever REMOVES. A comment it
reproduces is published exactly as the pipeline wrote it; one it cannot
reproduce is dropped. It does not apply the refuter's suggested rewording, and
it lowers a severity but never raises one. The same gate was built for the
macro issues and dropped after measurement — see docs/AGENTIC_REVIEW.md.
"""

from __future__ import annotations

import json

from coarse.agent.refutation import refute_comments
from coarse.types import DetailedComment, PaperStructure, SectionInfo, SectionType

QUOTE_A = "The displayed gradient has the opposite sign from the derivative."
QUOTE_B = "The curvature bound is half the exact curvature under these definitions."
BODY = f"{QUOTE_A} {QUOTE_B} Padding to make the section substantial. " * 12


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


class FakeClient:
    """Answers by role, keyed on the system prompt.

    ``comment_verdicts`` maps a comment title to the verdict to return for it.
    """

    def __init__(
        self,
        *,
        comment_verdicts: dict[str, str] | None = None,
    ) -> None:
        self.comment_verdicts = comment_verdicts or {}
        self.comment_tasks: list[str] = []
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

        if "check a single criticism" in system:
            self.comment_tasks.append(task)
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


def test_comments_sharing_a_number_are_judged_separately(tmp_path):
    """Refutation runs before ``_renumber_comments``.

    The numbers reaching this stage are whatever the editorial pass emitted,
    and on the double-failure fallback path they are raw section order with
    section-local numbering, so duplicates are expected. Keying the lookup on
    the number collapsed the maps and misattributed verdicts.
    """
    comments = [
        _comment(1, "Sign error", QUOTE_A),
        _comment(1, "Curvature", QUOTE_B),
        _comment(2, "Third point", QUOTE_A),
    ]
    kept, verdicts, records = refute_comments(
        comments,
        _paper(),
        _structure(),
        FakeClient(comment_verdicts={"Curvature": "refuted"}),
        max_parallel=1,
        workspace_root=str(tmp_path / "dup"),
    )
    assert [c.title for c in kept] == ["Sign error", "Third point"]
    assert len(verdicts) == 3, "each comment must get its own verdict"
    assert len(records) == 3
    assert len({v.finding_id for v in verdicts}) == 3, "ledger ids must be unique"


def test_a_surviving_comment_is_published_as_written(tmp_path):
    """The gate is subtractive.

    Applying the refuter's ``corrected_claim`` was measured to be where the
    stage's apparent precision gain came from, partly by retreating from an
    error claim to a request for clarification, so the suggestion is recorded
    and not applied.
    """

    class Rewrites(FakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            if "check a single criticism" in str(messages[0].get("content", "")):
                return _submit(
                    {
                        "finding_id": "x",
                        "verdict": "confirmed",
                        "reasoning": "Reproduced.",
                        "corrected_claim": "A softer restatement the author would read.",
                        "severity_after_review": "major",
                    }
                )
            return super().complete_with_tools(messages, tools, **kwargs)

    original = _comment(1, "Sign error", QUOTE_A)
    kept, verdicts, _r = refute_comments(
        [original],
        _paper(),
        _structure(),
        Rewrites(),
        max_parallel=1,
        workspace_root=str(tmp_path / "keep"),
    )
    assert kept[0].feedback == original.feedback
    assert verdicts[0].corrected_claim, "the suggestion is still recorded on the verdict"


def test_severity_is_lowered_but_never_raised(tmp_path):
    """``severity_after_review`` defaults to "major", so applying it
    unconditionally raised the severity of a minor comment the refuter never
    reconsidered."""

    class Verdicts(FakeClient):
        def __init__(self, severity: str) -> None:
            super().__init__()
            self.severity = severity

        def complete_with_tools(self, messages, tools, **kwargs):
            if "check a single criticism" in str(messages[0].get("content", "")):
                return _submit(
                    {
                        "finding_id": "x",
                        "verdict": "confirmed",
                        "reasoning": "r",
                        "severity_after_review": self.severity,
                    }
                )
            return super().complete_with_tools(messages, tools, **kwargs)

    critical = _comment(1, "Serious", QUOTE_A).model_copy(update={"severity": "critical"})
    kept, _v, _r = refute_comments(
        [critical],
        _paper(),
        _structure(),
        Verdicts("minor"),
        max_parallel=1,
        workspace_root=str(tmp_path / "sev1"),
    )
    assert kept[0].severity == "minor", "a downgrade is applied"

    minor = _comment(1, "Small", QUOTE_A).model_copy(update={"severity": "minor"})
    kept, _v, _r = refute_comments(
        [minor],
        _paper(),
        _structure(),
        Verdicts("major"),
        max_parallel=1,
        workspace_root=str(tmp_path / "sev2"),
    )
    assert kept[0].severity == "minor", "the default must not raise it"


def test_refute_comments_on_an_empty_list_is_a_noop():
    assert refute_comments([], _paper(), _structure(), FakeClient()) == ([], [], [])


def test_refute_comments_keeps_a_comment_whose_check_could_not_run(tmp_path):
    """An infrastructure failure must not silently delete a finding."""

    class Broken(FakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            if "check a single criticism" in str(messages[0].get("content", "")):
                raise RuntimeError("provider down")
            return super().complete_with_tools(messages, tools, **kwargs)

    kept, verdicts, _r = refute_comments(
        [_comment(1, "Sign error", QUOTE_A)],
        _paper(),
        _structure(),
        Broken(),
        max_parallel=1,
        workspace_root=str(tmp_path / "broken"),
    )
    assert [c.title for c in kept] == ["Sign error"]
    assert verdicts == []
