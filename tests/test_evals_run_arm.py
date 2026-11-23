"""The eval harness must actually request the paired round-1 arm.

The orchestrator's ``emit_round1_review`` flag was tested and passing while
``evals/run_arm.py`` never set it, so four paired runs produced no arm A and
exited 0: the save side is guarded by ``is_file()``, which skips in silence.
This test closes the gap between the two.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ARM = REPO_ROOT / "evals" / "run_arm.py"


def _load_run_arm():
    spec = importlib.util.spec_from_file_location("_eval_run_arm", RUN_ARM)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["_eval_run_arm"] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("rounds", "expected"), [(1, False), (2, True)])
def test_run_agent_requests_the_paired_arm_when_a_second_round_runs(
    rounds, expected, monkeypatch, tmp_path
):
    run_arm = _load_run_arm()
    seen: dict = {}

    def fake_run_agentic_review(markdown, structure, client, **kwargs):
        seen.update(kwargs)
        return ("review", [], object())

    monkeypatch.setitem(
        sys.modules,
        "coarse.agent.orchestrator",
        type(
            "M",
            (),
            {"run_agentic_review": staticmethod(fake_run_agentic_review)},
        ),
    )

    run_arm.run_agent(
        "# paper",
        object(),
        object(),
        mode="swarm",
        workspace_root=tmp_path / "w",
        max_targets=8,
        max_parallel=3,
        rounds=rounds,
    )

    assert seen["rounds"] == rounds
    assert seen["emit_round1_review"] is expected, (
        "a rounds=2 run must emit arm A, or the pairing is silently skipped"
    )
