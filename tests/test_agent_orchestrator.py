"""Tests for coarse.agent.orchestrator.

The behaviour that matters here is the refutation gate: a candidate finding
that an independent refuter does not reproduce must not reach the editor, and
must not reach the user. Everything is driven by a role-aware fake client, so
these run at zero provider cost.
"""

from __future__ import annotations

import json

import pytest

from coarse.agent.orchestrator import extract_labels, run_agentic_review
from coarse.types import PaperStructure, SectionInfo, SectionType

QUOTE_A = "The displayed gradient has the opposite sign from the derivative."
QUOTE_B = "The curvature bound is half the exact curvature under these definitions."
PROOF = f"{QUOTE_A} {QUOTE_B} Padding to make the section substantial. " * 12


def _structure() -> PaperStructure:
    return PaperStructure(
        title="A Paper",
        domain="statistics",
        taxonomy="academic/research_paper",
        abstract="An abstract about stable selection.",
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text="We study selection. " * 30,
                section_type=SectionType.INTRODUCTION,
            ),
            SectionInfo(
                number="A.10",
                title="Proof of Proposition 2",
                text=PROOF,
                section_type=SectionType.OTHER,
                math_content=True,
            ),
        ],
    )


def _paper() -> str:
    return f"# A Paper\n\n# 1 Introduction\n\nWe study selection.\n\n# A.10\n\n{PROOF}\n"


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


def _finding(fid: str, title: str, quote: str) -> dict:
    return {
        "finding_id": fid,
        "title": title,
        "location": "Appendix A.10",
        "claim": f"{title}: the step does not hold as written.",
        "why_it_matters": "The stated bound does not follow.",
        "remediation": "Correct the step.",
        "anchors": [{"section_id": "001", "quote": quote}],
        "severity": "major",
        "self_confidence": "high",
    }


class RoleFakeClient:
    """Answers according to the role it infers from the system prompt."""

    def __init__(self, *, verdicts: dict[str, str], findings: list[dict] | None = None) -> None:
        self.verdicts = verdicts
        self.findings = (
            findings
            if findings is not None
            else [
                _finding("f1", "Sign error", QUOTE_A),
                _finding("f2", "Curvature factor", QUOTE_B),
            ]
        )
        self.model = "fake/model"
        self.supports_prompt_caching = False
        self.editor_tasks: list[str] = []
        self.refuter_tasks: list[str] = []
        self._cost = 0.0

    @property
    def cost_usd(self) -> float:
        return self._cost

    def complete_with_tools(self, messages, tools, **_kwargs) -> dict:
        self._cost += 0.01
        system = str(messages[0].get("content", ""))
        task = str(messages[1].get("content", "")) if len(messages) > 1 else ""

        if "planning how a paper will be checked" in system:
            return _submit(
                {
                    "targets": [
                        {
                            "target_id": "x",
                            "question": "Check the gradient sign in A.10.",
                            "locations": ["Appendix A.10"],
                            "rationale": "Proof appendix.",
                        }
                    ]
                }
            )
        if "checking one specific thing" in system:
            return _submit({"findings": self.findings})
        if "check a single criticism" in system:
            self.refuter_tasks.append(task)
            # Route by which quote the claim points at.
            which = "f1" if "Sign error" in task else "f2"
            return _submit(
                {
                    "finding_id": which,
                    "verdict": self.verdicts.get(which, "confirmed"),
                    "reasoning": "Checked against the paper.",
                    "severity_after_review": "major",
                }
            )
        if "editor assembling" in system:
            self.editor_tasks.append(task)
            return _submit(
                {
                    "assessment": "The paper studies stable selection.",
                    "issues": [{"title": "Proof gap in A.10", "body": "The step does not hold."}],
                    "recommendation": "major revision",
                    "detailed_comments": [
                        {
                            "number": 1,
                            "title": "Sign error",
                            "quote": QUOTE_A,
                            "feedback": "The displayed derivative disagrees with the loss.",
                            "severity": "major",
                            "confidence": "high",
                        }
                    ],
                }
            )
        return {"role": "assistant", "content": "unrecognized role"}


def _run(client, tmp_path, **kwargs):
    return run_agentic_review(
        _paper(),
        _structure(),
        client,
        workspace_root=str(tmp_path / "ws"),
        keep_workspace=True,
        max_parallel=1,
        **kwargs,
    )


def test_extract_labels_finds_real_labels_and_not_following_words():
    labels = extract_labels(
        "Assumption that the design is fixed. Definition 2 states X. Lemma 3.3 gives Y. "
        "Theorem 1 follows. Algorithm 5 minimizes Z."
    )
    assert "Definition 2" in labels
    assert "Lemma 3.3" in labels
    assert "Theorem 1" in labels
    assert "Algorithm 5" in labels
    # "Assumption that ..." must not become the label "Assumption t".
    assert "Assumption t " not in labels
    assert "Assumption t\n" not in labels


def test_a_confirmed_finding_reaches_the_editor(tmp_path):
    client = RoleFakeClient(verdicts={"f1": "confirmed", "f2": "confirmed"})
    review, records, ws = _run(client, tmp_path)
    manifest = json.loads((ws.root / "run.json").read_text())
    assert manifest["candidate_findings"] == 2
    assert manifest["confirmed_findings"] == 2
    assert review.detailed_comments[0].title == "Sign error"
    assert {r.role for r in records} == {"planner", "investigator", "refuter", "editor"}


@pytest.mark.parametrize("bad_verdict", ["refuted", "inconclusive"])
def test_a_finding_the_refuter_does_not_reproduce_is_withheld(tmp_path, bad_verdict):
    """The gate against the pipeline's known failure mode.

    A candidate the independent refuter cannot reproduce must not be offered
    to the editor at all, so it cannot be written up however confident the
    investigator was.
    """
    client = RoleFakeClient(verdicts={"f1": "confirmed", "f2": bad_verdict})
    _review, _records, ws = _run(client, tmp_path)

    manifest = json.loads((ws.root / "run.json").read_text())
    assert manifest["candidate_findings"] == 2
    assert manifest["confirmed_findings"] == 1

    editor_task = client.editor_tasks[0]
    assert "Sign error" in editor_task
    assert "Curvature factor" not in editor_task, (
        "a finding that failed independent review was still shown to the editor"
    )


def test_every_candidate_is_refuted_exactly_once(tmp_path):
    client = RoleFakeClient(verdicts={"f1": "confirmed", "f2": "confirmed"})
    _run(client, tmp_path)
    assert len(client.refuter_tasks) == 2


def test_the_refuter_is_not_shown_the_investigators_reasoning(tmp_path):
    """Independence is the point: a refuter shown the derivation audits the
    derivation instead of the paper."""
    findings = [_finding("f1", "Sign error", QUOTE_A)]
    findings[0]["computation"] = "SECRET_TRANSCRIPT sympy says diff is negative"
    client = RoleFakeClient(verdicts={"f1": "confirmed"}, findings=findings)
    _run(client, tmp_path)

    task = client.refuter_tasks[0]
    assert "SECRET_TRANSCRIPT" not in task
    assert "Suggested fix" not in task
    # It does get the claim and the paper passage, which are what it checks.
    assert "Sign error" in task
    assert QUOTE_A in task


def test_single_mode_skips_planning_and_refutation(tmp_path):
    client = RoleFakeClient(verdicts={})
    _review, records, ws = _run(client, tmp_path, mode="single")
    roles = {r.role for r in records}
    assert "planner" not in roles
    assert "refuter" not in roles
    manifest = json.loads((ws.root / "run.json").read_text())
    assert manifest["mode"] == "single"
    # Unrefuted findings still reach the editor in this mode, by design: the
    # arm exists to measure what retrieval and computation alone are worth.
    assert manifest["confirmed_findings"] == 2


def test_all_findings_refuted_yields_an_explicit_no_issues_review(tmp_path):
    client = RoleFakeClient(verdicts={"f1": "refuted", "f2": "refuted"})
    review, _records, ws = _run(client, tmp_path)
    manifest = json.loads((ws.root / "run.json").read_text())
    assert manifest["confirmed_findings"] == 0
    assert review.overall_feedback.issues, "a Review requires at least one issue"


def test_an_editor_failure_falls_back_to_rendering_the_ledger(tmp_path):
    class NoEditor(RoleFakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            if "editor assembling" in str(messages[0].get("content", "")):
                raise RuntimeError("editor provider down")
            return super().complete_with_tools(messages, tools, **kwargs)

    client = NoEditor(verdicts={"f1": "confirmed", "f2": "confirmed"})
    review, _records, _ws = _run(client, tmp_path)
    titles = {c.title for c in review.detailed_comments}
    assert {"Sign error", "Curvature factor"} <= titles, (
        "confirmed findings must survive an editor failure"
    )
    assert all(len(c.quote) >= 20 for c in review.detailed_comments)


def test_a_planner_failure_falls_back_to_a_whole_paper_target(tmp_path):
    class NoPlan(RoleFakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            if "planning how a paper will be checked" in str(messages[0].get("content", "")):
                return _submit({"targets": []})
            return super().complete_with_tools(messages, tools, **kwargs)

    client = NoPlan(verdicts={"f1": "confirmed", "f2": "confirmed"})
    _review, _records, ws = _run(client, tmp_path)
    manifest = json.loads((ws.root / "run.json").read_text())
    assert manifest["targets"][0]["target_id"] == "t01"
    assert manifest["candidate_findings"] == 2


def test_comments_are_renumbered_sequentially(tmp_path):
    client = RoleFakeClient(verdicts={"f1": "confirmed", "f2": "confirmed"})
    review, _records, _ws = _run(client, tmp_path)
    assert [c.number for c in review.detailed_comments] == list(
        range(1, len(review.detailed_comments) + 1)
    )


def test_the_manifest_records_per_agent_accounting(tmp_path):
    client = RoleFakeClient(verdicts={"f1": "confirmed", "f2": "confirmed"})
    _review, records, ws = _run(client, tmp_path)
    manifest = json.loads((ws.root / "run.json").read_text())
    assert manifest["model"] == "fake/model"
    assert len(manifest["agents"]) == len(records)
    assert manifest["cost_usd"] > 0
    # Ledger ids are reassigned from the target, so they are collision-free
    # across investigators regardless of what the model returned.
    assert set(manifest["verdicts"]) == {"t01-f1", "t01-f2"}
