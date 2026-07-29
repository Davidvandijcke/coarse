"""Tests for the canonical pipeline stage spec."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from coarse.config import CoarseConfig
from coarse.cost import build_cost_estimate
from coarse.llm import model_cost_per_token
from coarse.models import (
    DEFAULT_MODEL,
    FUSION_INPUT_COST_PER_TOKEN,
    FUSION_MODEL,
    FUSION_OUTPUT_COST_PER_TOKEN,
)
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


def test_dynamic_pricing_overrides_exported_for_fusion():
    # The web estimator substitutes these when OpenRouter returns -1 pricing.
    # They must match the canonical rates in models.py so web/Python don't drift.
    overrides = export_web_spec()["dynamicPricingOverrides"]
    assert overrides[FUSION_MODEL] == {
        "prompt": FUSION_INPUT_COST_PER_TOKEN,
        "completion": FUSION_OUTPUT_COST_PER_TOKEN,
    }


def _run_ts_estimator(
    repo_root: Path,
    total_tokens: int,
    model_id: str,
    is_pdf: bool,
    section_count: int | None,
    has_openrouter_key: bool,
    deep_literature_search: bool,
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
  {str(deep_literature_search).lower()},
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
            "deep_literature_search": False,
        },
        {
            "model_id": "openai/gpt-5-pro",
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": False,
            "deep_literature_search": False,
        },
        # #185: exercise the reasoning carve-out boundary in BOTH estimators.
        # gpt-5.4 is now reasoning (broad gpt-5 prefix) → +overhead; gpt-5-chat
        # is the non-reasoning carve-out → no overhead. With nonzero per-token
        # pricing, any TS/Python divergence on the reasoning flag would break
        # the dollar-total parity below.
        {
            "model_id": "openai/gpt-5.4",
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": True,
            "deep_literature_search": False,
        },
        {
            "model_id": "openai/gpt-5-chat",
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": True,
            "deep_literature_search": False,
        },
        # OpenRouter Fusion: dynamic (-1) OpenRouter pricing, substituted with
        # representative rates. Verifies both estimators price it identically
        # (and positively) rather than going to $0 / negative.
        {
            "model_id": FUSION_MODEL,
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": True,
            "deep_literature_search": False,
        },
        {
            "model_id": DEFAULT_MODEL,
            "section_count": 18,
            "is_pdf": False,
            "has_openrouter_key": True,
            "deep_literature_search": True,
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
            deep_literature_search=scenario["deep_literature_search"],
        ).total_cost_usd
        ts_total = _run_ts_estimator(
            repo_root,
            total_tokens=paper_text.token_estimate,
            model_id=scenario["model_id"],
            is_pdf=scenario["is_pdf"],
            section_count=scenario["section_count"],
            has_openrouter_key=scenario["has_openrouter_key"],
            deep_literature_search=scenario["deep_literature_search"],
        )
        assert abs(ts_total - py_total) < 1e-9


def _run_node(repo_root: Path, script: str) -> object:
    """Run an ESM snippet through node's type-stripping loader; parse its stdout JSON."""
    result = subprocess.run(
        ["node", "--experimental-strip-types", "--input-type=module", "-e", script],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_ts_pricing_map_handles_dynamic_negative_pricing():
    """estimateCost.fetchPricingMap must not let OpenRouter's "-1" dynamic
    price reach the estimator: a known dynamic model (Fusion) is substituted
    with representative rates, an unknown dynamic model is dropped (→ null →
    "cost estimate unavailable"), and normal models pass through. Exercises the
    web-side fix that the Python parity test can't (it injects rates directly)."""
    repo_root = Path(__file__).resolve().parents[1]
    script = """
globalThis.fetch = async () => ({
  json: async () => ({ data: [
    { id: "anthropic/claude-test", pricing: { prompt: "0.000003", completion: "0.000015" } },
    { id: "openrouter/fusion", pricing: { prompt: "-1", completion: "-1" } },
    { id: "openrouter/auto", pricing: { prompt: "-1", completion: "-1" } },
  ]})
});
const { getModelPricing } = await import("./web/src/lib/estimateCost.ts");
console.log(JSON.stringify({
  normal: await getModelPricing("anthropic/claude-test"),
  fusion: await getModelPricing("openrouter/fusion"),
  unknownDynamic: await getModelPricing("openrouter/auto"),
}));
"""
    out = _run_node(repo_root, script)
    assert out["normal"] == {"promptCostPerToken": 3e-6, "completionCostPerToken": 1.5e-5}
    assert out["fusion"] == {
        "promptCostPerToken": FUSION_INPUT_COST_PER_TOKEN,
        "completionCostPerToken": FUSION_OUTPUT_COST_PER_TOKEN,
    }
    # Unknown dynamic model is omitted → getModelPricing returns null, NOT a
    # negative rate. This is the regression guard for the $-743986 UI bug.
    assert out["unknownDynamic"] is None


def test_ts_token_estimator_is_script_aware_and_matches_python():
    """The web token estimator (estimateTokensFromString) must mirror Python's
    textscript.estimate_tokens: identical to len//4 for Latin, ~4-6x higher for
    CJK. This keeps the web cost quote in sync with the CLI on CJK papers."""
    from coarse.textscript import estimate_tokens

    repo_root = Path(__file__).resolve().parents[1]
    latin = "The quick brown fox jumps over the lazy dog. " * 100
    cjk = "这是一篇中文论文的摘要内容" * 100
    script = f"""
import {{ estimateTokensFromString }} from "./web/src/lib/estimateCost.ts";
console.log(JSON.stringify({{
  latin: estimateTokensFromString({json.dumps(latin)}),
  cjk: estimateTokensFromString({json.dumps(cjk)}),
}}));
"""
    out = _run_node(repo_root, script)
    # TS↔Python parity on the token count itself.
    assert out["latin"] == estimate_tokens(latin)
    assert out["cjk"] == estimate_tokens(cjk)
    # Latin invariant: equals the old len//4.
    assert out["latin"] == len(latin) // 4
    # CJK materially higher than the old len//4 under-count (2.5x with the
    # keystone's 1.6 vs 4 chars/token constants).
    assert out["cjk"] >= (len(cjk) // 4) * 2


def test_ts_token_estimator_handles_supplementary_plane_cjk():
    """A supplementary-plane ideograph (CJK Ext B+) is one CJK character in both
    estimators — TS iterates code points, not UTF-16 units, matching Python."""
    from coarse.textscript import estimate_tokens

    repo_root = Path(__file__).resolve().parents[1]
    # U+20000 (𠀀) repeated — purely supplementary-plane Han.
    cjk_supp = "\U00020000" * 50
    script = f"""
import {{ estimateTokensFromString }} from "./web/src/lib/estimateCost.ts";
console.log(JSON.stringify(estimateTokensFromString({json.dumps(cjk_supp)})));
"""
    out = _run_node(repo_root, script)
    assert out == estimate_tokens(cjk_supp)
    assert out == int(50 / 1.6)  # 50 CJK chars at ~1.6 chars/token, not 100


def test_ts_format_prompt_price_branches():
    repo_root = Path(__file__).resolve().parents[1]
    script = """
import { formatPromptPrice } from "./web/src/lib/estimateCost.ts";
console.log(JSON.stringify({
  dynamic: formatPromptPrice(-1),
  free: formatPromptPrice(0),
  cheap: formatPromptPrice(2.6e-7),
  pricey: formatPromptPrice(5e-6),
  unknown: formatPromptPrice(null),
  nan: formatPromptPrice(NaN),
}));
"""
    out = _run_node(repo_root, script)
    assert out == {
        "dynamic": "variable",
        "free": "free",
        "cheap": "$0.26/M",
        "pricey": "$5/M",
        "unknown": "",
        "nan": "",
    }
