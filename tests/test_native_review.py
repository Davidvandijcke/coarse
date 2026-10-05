"""Native checkpoints reuse the real pipeline without model/network subprocesses."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from coarse.native_install import install_skill
from coarse.native_review import advance, prepare, publish, status, submit
from coarse.native_store import atomic_json, read_json, workspace_lock

QUOTE = "The sample mean has variance sigma squared divided by n squared."
PAPER = f"""# Synthetic variance paper

## Introduction

We estimate an independent sample mean. {QUOTE} This calculation determines our intervals.

## Methodology

Proposition 1. {QUOTE} Proof: add the independent variances, then divide by n squared.
We claim the sum has variance sigma squared, without the factor n.
The observations have equal marginal variance.

## Conclusion

We use the claimed standard error in a confidence interval with nominal 95 percent coverage.
We claim the interval is calibrated at every sample size. {QUOTE}
"""


def fixture_answer(task):
    """Mechanical fixture for control-flow tests, never a model-quality result."""
    schema = task["response_schema"]

    def make(node, key=""):
        if "$ref" in node:
            return make(schema["$defs"][node["$ref"].split("/")[-1]], key)
        if "anyOf" in node:
            return make(next(n for n in node["anyOf"] if n.get("type") != "null"), key)
        if "const" in node:
            return node["const"]
        if "enum" in node:
            return node["enum"][0]
        if node.get("type") == "object":
            return {k: make(v, k) for k, v in node.get("properties", {}).items()}
        if node.get("type") == "array":
            if key == "math_section_indices":
                return [2]
            return [make(node["items"], key) for _ in range(max(1, node.get("minItems", 0)))]
        if node.get("type") == "integer":
            return max(1, node.get("minimum", 0))
        if node.get("type") == "number":
            return max(0.5, node.get("minimum", 0))
        if node.get("type") == "boolean":
            return True
        if key == "quote":
            return QUOTE
        if key == "language":
            return "en"
        if key == "domain":
            return "social_sciences/economics"
        if key == "taxonomy":
            return "academic/research_paper"
        return "Synthetic test response. " * max(2, node.get("minLength", 0) // 20 + 1)

    if task["response_type"] == "NativeLiterature":
        return {
            "searched": False,
            "context": "Search deliberately unavailable in fixture.",
            "sources": [],
        }
    return make(schema)


@pytest.fixture
def paper(tmp_path):
    p = tmp_path / "input.md"
    p.write_text(PAPER)
    return p


def finish(workspace, seen=None):
    for _ in range(30):
        state = advance(workspace)
        if state["status"] == "ready":
            return state
        assert state["tasks"], state
        for entry in state["tasks"]:
            task = read_json(Path(entry["file"]))
            if seen is not None:
                seen.add(task["response_type"])
            submit(workspace, task["task_id"], fixture_answer(task), agent_id="fixture-agent")
    pytest.fail("Native pipeline failed to reach readiness within 30 task batches")


@pytest.mark.parametrize("host", ["codex", "claude"])
def test_full_native_pipeline_never_invokes_provider_clients_or_network(tmp_path, paper, host):
    workspace = tmp_path / "review"
    with (
        patch("coarse.pipeline.LLMClient", side_effect=AssertionError("provider client called")),
        patch("requests.get", side_effect=AssertionError("unexpected network")),
        patch("requests.post", side_effect=AssertionError("unexpected network")),
        patch("subprocess.Popen", side_effect=AssertionError("unexpected CLI subprocess")),
    ):
        first = prepare(workspace, paper=paper, host=host)
        assert first["status"] == "waiting"
        assert first["completed_tasks"] == 0
        with pytest.raises(ValueError, match="every required task"):
            publish(workspace)
        seen = set()
        final = finish(workspace, seen)
        assert final["publication"] == "not_requested"
        assert final["subscription_usage"] is None
        assert final["completed_tasks"] >= 10
        assert "NativeLiterature" in seen
        assert "OverviewFeedback" in seen
        assert "_SectionComments" in seen
        assert any("Verif" in name or "Proof" in name for name in seen), seen
        assert any("Editorial" in name for name in seen), seen
        original = (workspace / "review.md").read_text()
        assert original
        assert advance(workspace)["status"] == "ready"
        assert (workspace / "review.md").read_text() == original
        assert status(workspace)["host"] == host
        with pytest.raises(ValueError, match="no website handoff"):
            publish(workspace)


def test_invalid_response_stays_pending_and_retry_is_idempotent(tmp_path, paper):
    w = tmp_path / "review"
    s = prepare(w, paper=paper, host="codex")
    task = read_json(Path(s["tasks"][0]["file"]))
    tid = task["task_id"]
    with pytest.raises(ValueError):
        submit(w, tid, {}, agent_id="test-agent")
    assert not list((w / "results").glob("*.json"))
    assert advance(w)["tasks"][0]["task_id"] == tid
    answer = fixture_answer(task)
    submit(w, tid, answer, agent_id="test-agent")
    submit(w, tid, answer, agent_id="test-agent")
    with pytest.raises(ValueError, match="immutable"):
        submit(w, tid, {**answer, "title": "Revised title"}, agent_id="test-agent")


def test_resume_rejects_changed_paper_and_task(tmp_path, paper):
    w = tmp_path / "review"
    s = prepare(w, paper=paper, host="codex")
    task_path = Path(s["tasks"][0]["file"])
    task = read_json(task_path)
    task["messages"][0]["content"] = "Modified instructions"
    atomic_json(task_path, task)
    with pytest.raises(ValueError, match="Task changed"):
        advance(w)
    (w / "paper.md").write_text("A changed source")
    with pytest.raises(ValueError, match="paper changed"):
        advance(w)


def test_corrupted_answer_cannot_be_swallowed_by_optional_stage_fallback(tmp_path, paper):
    w = tmp_path / "review"
    s = prepare(w, paper=paper, host="codex")
    tid = s["tasks"][0]["task_id"]
    (w / "results" / f"{tid}.json").write_text("not JSON")
    with pytest.raises(ValueError, match="checkpoint failed validation"):
        advance(w)
    assert not (w / "review.md").exists()


def test_requested_model_and_effort_are_checked(tmp_path, paper):
    w = tmp_path / "review"
    s = prepare(w, paper=paper, host="codex", model="test-model", effort="high")
    task = read_json(Path(s["tasks"][0]["file"]))
    answer = fixture_answer(task)
    with pytest.raises(ValueError, match="model"):
        submit(w, task["task_id"], answer, agent_id="a", reported_model="wrong")
    with pytest.raises(ValueError, match="effort"):
        submit(w, task["task_id"], answer, agent_id="a", reported_model="test-model")
    submit(
        w,
        task["task_id"],
        answer,
        agent_id="a",
        reported_model="test-model",
        reported_effort="high",
    )


def test_workspace_lock_and_existing_workspace_protection(tmp_path, paper):
    w = tmp_path / "review"
    prepare(w, paper=paper, host="codex")
    with pytest.raises(ValueError, match="already exists"):
        prepare(w, paper=paper, host="codex")
    with workspace_lock(w):
        with pytest.raises(ValueError, match="Another coordinator"):
            advance(w)


@pytest.mark.parametrize("host", ["codex", "claude"])
def test_install_native_skill_preserves_existing_headless_skill(tmp_path, host):
    root = tmp_path / (".codex" if host == "codex" else ".claude") / "skills"
    old = root / "coarse-review/SKILL.md"
    old.parent.mkdir(parents=True)
    old.write_text("existing")
    result = install_skill(host, home=tmp_path)
    assert old.read_text() == "existing"
    installed = Path(result["skill_file"])
    assert installed.exists()
    installed.write_text("custom")
    with pytest.raises(ValueError, match="differs"):
        install_skill(host, home=tmp_path)
    install_skill(host, home=tmp_path, force=True)
    assert installed.read_text() != "custom"


def test_handoff_publish_is_explicit_idempotent_and_uncertain_on_lost_ack(tmp_path, paper):
    bundle = {
        "paper_id": "test",
        "finalize_token": "secret",
        "callback_url": "https://example.test/finalize",
    }

    def prepared(name):
        w = tmp_path / name
        with (
            patch("coarse.native_review._fetch_handoff", return_value=bundle),
            patch("coarse.native_review._download_handoff_source", return_value=paper),
        ):
            prepare(w, handoff="https://example.test/h/test", host="codex")
        finish(w)
        return w

    with patch(
        "coarse.native_review._post_finalize",
        return_value={"review_url": "https://example.test/review/test"},
    ) as post:
        w = prepared("success")
        post.assert_not_called()
        assert publish(w)["publication"] == "published"
        assert publish(w)["publication"] == "published"
        assert post.call_count == 1
    with patch("coarse.native_review._post_finalize", side_effect=OSError("lost ack")) as post:
        w = prepared("lost")
        with pytest.raises(OSError):
            publish(w)
        with pytest.raises(ValueError, match="uncertain"):
            publish(w)
        assert post.call_count == 1
        assert status(w)["publication"] == "uncertain"


def test_plugin_and_wheel_skill_match():
    root = Path(__file__).resolve().parents[1]
    assert (
        root / "plugins/coarse-native-review/skills/coarse-native-review/SKILL.md"
    ).read_bytes() == (root / "src/coarse/_skills/native_review/SKILL.md").read_bytes()


def test_pdf_publication_requires_host_extraction_inspection(tmp_path, paper):
    from coarse.native_review import confirm_extraction

    pdf = tmp_path / "source.pdf"
    pdf.write_bytes(b"%PDF-1.7\nsynthetic transport fixture")
    workspace = tmp_path / "pdf-review"
    prepare(workspace, paper=pdf, pre_extracted=paper, host="claude")
    assert status(workspace)["pdf_visual_qa"] == "requires_host_check"
    finish(workspace)
    with pytest.raises(ValueError, match="confirm-extraction"):
        publish(workspace)
    confirm_extraction(workspace, agent_id="fixture-inspector", notes="Synthetic check receipt")
    assert status(workspace)["pdf_visual_qa"] == "host_checked"
    with pytest.raises(ValueError, match="no website handoff"):
        publish(workspace)


def test_checkpoint_refuses_a_different_engine_and_original_source(tmp_path, paper):
    workspace = tmp_path / "review"
    prepare(workspace, paper=paper, host="codex")
    with patch("coarse.native_store.engine_digest", return_value="different-code"):
        with pytest.raises(ValueError, match="original Coarse code"):
            advance(workspace)
    (workspace / "source.md").write_text("Changed original")
    with pytest.raises(ValueError, match="Original source changed"):
        advance(workspace)


def test_resume_returns_same_tasks_without_duplicate_side_effects(tmp_path, paper):
    workspace = tmp_path / "review"
    first = prepare(workspace, paper=paper, host="codex")
    second = advance(workspace)
    assert first["tasks"] == second["tasks"]
    assert first["runner_prefix"] == second["runner_prefix"]
    assert len(list((workspace / "tasks").glob("*.json"))) == 1
    assert not list((workspace / "results").glob("*.json"))


def test_empty_successful_findings_are_not_logged_as_failed_agents(
    tmp_path, paper, monkeypatch, caplog
):
    import sys

    original = fixture_answer

    def empty_comments(task):
        answer = original(task)
        if "comments" in answer:
            answer["comments"] = []
        return answer

    monkeypatch.setattr(sys.modules[__name__], "fixture_answer", empty_comments)
    workspace = tmp_path / "empty-findings"
    prepare(workspace, paper=paper, host="codex")
    assert finish(workspace)["status"] == "ready"
    assert read_json(workspace / "review.json")["detailed_comments"] == []
    assert "All section agents failed" not in caplog.text
