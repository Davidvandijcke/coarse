"""Tests for the canonical pipeline stage spec."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from coarse.config import CoarseConfig
from coarse.cost import build_cost_estimate
from coarse.llm import model_cost_per_token
from coarse.models import DEFAULT_MODEL
from coarse.pipeline_spec import (
    MAX_REVIEWABLE_SECTIONS,
    estimate_cross_section_count,
    estimate_math_section_count,
    estimate_section_count,
    export_web_spec,
)
from coarse.types import PaperText


def test_section_count_caps_at_runtime_limit():
    assert estimate_section_count(999_999) == MAX_REVIEWABLE_SECTIONS


def test_math_and_cross_section_heuristics_are_stable():
    assert estimate_math_section_count(8) == 2
    assert estimate_cross_section_count(5) == 0
    assert estimate_cross_section_count(6) == 1
    assert estimate_cross_section_count(12) == 2
    assert estimate_cross_section_count(18) == 3


def test_exported_web_spec_matches_checked_in_json():
    repo_root = Path(__file__).resolve().parents[1]
    json_path = repo_root / "web" / "src" / "data" / "pipelineSpec.json"
    checked_in = json.loads(json_path.read_text())
    assert checked_in == export_web_spec()


def _run_ts_estimator(
    repo_root: Path,
    total_tokens: int,
    model_id: str,
    is_pdf: bool,
    section_count: int | None,
    has_openrouter_key: bool,
) -> float:
    prompt_cost, completion_cost = model_cost_per_token(model_id)
    section_arg = "undefined" if section_count is None else str(section_count)
    script = f"""
import {{ estimateReviewCost }} from "./web/src/lib/estimateCost.ts";

const total = estimateReviewCost(
  {total_tokens},
  {{
    promptCostPerToken: {prompt_cost},
    completionCostPerToken: {completion_cost},
  }},
  "{model_id}",
  {str(is_pdf).lower()},
  {section_arg},
  {str(has_openrouter_key).lower()},
);
console.log(JSON.stringify(total));
"""
    result = subprocess.run(
        ["node", "--experimental-strip-types", "--input-type=module", "-e", script],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout))


def test_ts_estimator_matches_python_cost_gate_for_openrouter_and_fallback_paths(monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    paper_text = PaperText(full_markdown="x" * 4000, token_estimate=40_000)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    scenarios = [
        {
            "model_id": DEFAULT_MODEL,
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": True,
        },
        {
            "model_id": "openai/gpt-5-pro",
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": False,
        },
    ]

    for scenario in scenarios:
        config = CoarseConfig(
            default_model=scenario["model_id"],
            extraction_qa=True,
            api_keys={"openrouter": "key"} if scenario["has_openrouter_key"] else {},
        )
        py_total = build_cost_estimate(
            paper_text,
            config,
            section_count=scenario["section_count"],
            is_pdf=scenario["is_pdf"],
            model=scenario["model_id"],
        ).total_cost_usd
        ts_total = _run_ts_estimator(
            repo_root,
            total_tokens=paper_text.token_estimate,
            model_id=scenario["model_id"],
            is_pdf=scenario["is_pdf"],
            section_count=scenario["section_count"],
            has_openrouter_key=scenario["has_openrouter_key"],
        )
        assert abs(ts_total - py_total) < 1e-9
