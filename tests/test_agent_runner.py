"""Tests for coarse.agent.runner — the tool loop, driven by a fake client.

No provider calls: the fake client replays a scripted sequence of assistant
messages, so the loop's control flow is covered deterministically at zero cost
(#264).
"""

from __future__ import annotations

import json

import pytest
from pydantic import BaseModel, Field

from coarse.agent.runner import run_agent
from coarse.agent.tools import ToolBox
from coarse.agent.workspace import ReviewWorkspace
from coarse.types import PaperStructure, SectionInfo, SectionType

BODY = "The needle is in this proof section. " * 30


class _Answer(BaseModel):
    answer: str = Field(default="")
    count: int = Field(default=0)


class FakeClient:
    """Replays scripted assistant messages and records what it was sent."""

    def __init__(self, script: list[dict], *, cost_per_turn: float = 0.01) -> None:
        self.script = list(script)
        self.calls: list[list[dict]] = []
        self.tools_sent: list[list[dict]] = []
        self._cost = 0.0
        self._cost_per_turn = cost_per_turn
        self.model = "fake/model"
        self.supports_prompt_caching = False

    @property
    def cost_usd(self) -> float:
        return self._cost

    def complete_with_tools(self, messages, tools, **_kwargs) -> dict:
        self.calls.append([dict(m) for m in messages])
        self.tools_sent.append(list(tools))
        self._cost += self._cost_per_turn
        if not self.script:
            return {"role": "assistant", "content": "I have nothing further."}
        return self.script.pop(0)


def _tool_call(name: str, args: dict, call_id: str = "c1") -> dict:
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": call_id,
                "type": "function",
                "function": {"name": name, "arguments": json.dumps(args)},
            }
        ],
    }


def _structure() -> PaperStructure:
    return PaperStructure(
        title="A Paper",
        domain="statistics",
        taxonomy="academic/research_paper",
        abstract="An abstract.",
        sections=[
            SectionInfo(
                number="A.10",
                title="Proof",
                text=BODY,
                section_type=SectionType.OTHER,
                math_content=True,
            )
        ],
    )


@pytest.fixture
def box(tmp_path):
    ws = ReviewWorkspace.create(
        f"# A Paper\n\n# A.10\n\n{BODY}\n", _structure(), root=tmp_path / "w"
    )
    yield ToolBox(workspace=ws, max_calls=20)
    ws.cleanup()


def _run(client, box, **kwargs):
    return run_agent(
        client,
        role="investigator",
        agent_id="t01",
        system="You are a referee.",
        task="Check the proof.",
        toolbox=box,
        submit_model=_Answer,
        **kwargs,
    )


def test_submit_returns_the_typed_result(box):
    client = FakeClient([_tool_call("submit", {"answer": "found it", "count": 1})])
    result = _run(client, box)
    assert isinstance(result.result, _Answer)
    assert result.result.answer == "found it"
    assert result.record.error == ""


def test_tool_results_are_fed_back_before_submission(box):
    client = FakeClient(
        [
            _tool_call("paper_search", {"query": "needle"}, "a"),
            _tool_call("submit", {"answer": "done"}, "b"),
        ]
    )
    result = _run(client, box)
    assert result.result.answer == "done"
    assert result.record.tool_calls == 1
    # The second request must carry the tool result from the first turn.
    second = client.calls[1]
    tool_msgs = [m for m in second if m.get("role") == "tool"]
    assert tool_msgs and "char_start=" in tool_msgs[0]["content"]


def test_a_rejected_submission_is_sent_back_for_repair(box):
    """A schema violation must become feedback, not a lost agent run."""
    client = FakeClient(
        [
            _tool_call("submit", {"count": "not-an-integer"}, "a"),
            _tool_call("submit", {"answer": "second try", "count": 2}, "b"),
        ]
    )
    result = _run(client, box)
    assert result.result.answer == "second try"
    rejection = [
        m
        for call in client.calls
        for m in call
        if m.get("role") == "tool" and "SUBMIT REJECTED" in str(m.get("content"))
    ]
    assert rejection, "the agent should have been told why its submission failed"


def test_malformed_tool_arguments_are_reported_to_the_agent(box):
    bad = {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "a",
                "type": "function",
                "function": {"name": "paper_search", "arguments": "{not json"},
            }
        ],
    }
    client = FakeClient([bad, _tool_call("submit", {"answer": "ok"}, "b")])
    result = _run(client, box)
    assert result.result.answer == "ok"
    assert any(
        "not valid JSON" in str(m.get("content"))
        for call in client.calls
        for m in call
        if m.get("role") == "tool"
    )


def test_an_agent_that_stops_talking_is_prompted_to_submit(box):
    client = FakeClient(
        [
            {"role": "assistant", "content": "Here is my prose answer."},
            _tool_call("submit", {"answer": "after nudge"}, "b"),
        ]
    )
    result = _run(client, box)
    assert result.result.answer == "after nudge"


def test_never_submitting_yields_no_result_and_an_explanation(box):
    client = FakeClient([{"role": "assistant", "content": "Just prose."}] * 6)
    result = _run(client, box, max_turns=3)
    assert result.result is None
    assert "no result submitted" in result.record.error
    assert result.text == "Just prose."


def test_a_provider_failure_is_recorded_rather_than_raised(box):
    class Boom(FakeClient):
        def complete_with_tools(self, messages, tools, **kwargs):
            raise RuntimeError("502 upstream")

    result = _run(Boom([]), box)
    assert result.result is None
    assert "502 upstream" in result.record.error


def test_the_record_accounts_for_cost_turns_and_tools(box):
    client = FakeClient(
        [
            _tool_call("paper_outline", {}, "a"),
            _tool_call("python", {"code": "print(1)"}, "b"),
            _tool_call("submit", {"answer": "x"}, "c"),
        ],
        cost_per_turn=0.25,
    )
    result = _run(client, box)
    assert result.record.turns == 3
    assert result.record.tool_calls == 2
    assert result.record.cost_usd == pytest.approx(0.75)
    assert result.record.duration_s >= 0
    assert result.record.model == "fake/model"


def test_the_submit_tool_is_offered_alongside_the_toolbox(box):
    client = FakeClient([_tool_call("submit", {"answer": "x"})])
    _run(client, box)
    offered = {t["function"]["name"] for t in client.tools_sent[0]}
    assert "submit" in offered
    assert {"paper_search", "paper_read", "paper_outline", "python"} <= offered


def test_the_submit_schema_carries_the_result_model(box):
    client = FakeClient([_tool_call("submit", {"answer": "x"})])
    _run(client, box)
    submit = next(t for t in client.tools_sent[0] if t["function"]["name"] == "submit")
    assert submit["function"]["parameters"] == _Answer.model_json_schema()
