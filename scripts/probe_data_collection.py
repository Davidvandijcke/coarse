"""Probe OpenRouter `data_collection` and `zdr` provider routing per model.

Sends a minimal 1-token completion for each model with
`provider: {"data_collection": "deny"}` (and separately `zdr: true`) and
reports which models still have a routable endpoint under each constraint.

Cost: ~$0.01 total (one 1-token call per model per constraint).

Usage: uv run python scripts/probe_data_collection.py
"""

from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv

from coarse.models import (
    CLAUDE_OPUS_5_MODEL,
    CLAUDE_SONNET_5_MODEL,
    DEEP_LITERATURE_SEARCH_MODEL,
    GEMINI_3_6_FLASH_MODEL,
    GPT_5_6_LUNA_MODEL,
    GPT_5_6_SOL_MODEL,
    GPT_5_6_TERRA_MODEL,
    GROK_4_5_MODEL,
    KIMI_K3_MODEL,
    LITERATURE_SEARCH_MODEL,
    QWEN_3_7_PLUS_MODEL,
)

load_dotenv()

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    sys.exit("OPENROUTER_API_KEY not set")

# Current user-visible defaults from web/src/components/ModelPicker.tsx plus
# the server-side literature models. Keep this probe aligned with each model
# refresh so privacy-routing checks exercise what users can actually select.
MODELS = [
    "anthropic/claude-fable-5",
    CLAUDE_OPUS_5_MODEL,
    CLAUDE_SONNET_5_MODEL,
    GPT_5_6_SOL_MODEL,
    GPT_5_6_TERRA_MODEL,
    GPT_5_6_LUNA_MODEL,
    "google/gemini-3.1-pro-preview",
    GEMINI_3_6_FLASH_MODEL,
    QWEN_3_7_PLUS_MODEL,
    KIMI_K3_MODEL,
    "deepseek/deepseek-v4-pro",
    GROK_4_5_MODEL,
    "meta-llama/llama-4-maverick",
    "z-ai/glm-5.2",
    "openrouter/fusion",
    LITERATURE_SEARCH_MODEL,
    DEEP_LITERATURE_SEARCH_MODEL,
]

CONSTRAINTS = [
    ("baseline", {}),
    ("data_collection=deny", {"data_collection": "deny"}),
    ("zdr=true", {"zdr": True}),
]


def probe(model: str, provider: dict) -> tuple[str, str]:
    """Return (status, detail). status is 'ok', 'no_endpoints', or 'other_error'."""
    body: dict = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "temperature": 0,
    }
    if provider:
        body["provider"] = provider
    try:
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=body,
            timeout=30.0,
        )
    except Exception as e:
        return ("network_error", str(e)[:100])
    if r.status_code == 200:
        return ("ok", "")
    # Parse error
    try:
        err = r.json().get("error", {})
        msg = err.get("message", r.text)[:150]
    except Exception:
        msg = r.text[:150]
    # OpenRouter returns 404 "No endpoints found" when routing constraints exclude all providers
    if r.status_code == 404 and "endpoint" in msg.lower():
        return ("no_endpoints", msg)
    return (f"http_{r.status_code}", msg)


def main() -> None:
    # Header
    w = 32
    print(f"{'model':<{w}} {'baseline':<12} {'deny':<18} {'zdr':<18}")
    print("-" * (w + 50))
    for model in MODELS:
        results = {}
        for label, provider in CONSTRAINTS:
            status, detail = probe(model, provider)
            results[label] = (status, detail)
        base = results["baseline"][0]
        deny = results["data_collection=deny"][0]
        zdr = results["zdr=true"][0]

        def fmt(s: str) -> str:
            if s == "ok":
                return "ok"
            if s == "no_endpoints":
                return "NO ENDPOINTS"
            return s

        print(f"{model:<{w}} {fmt(base):<12} {fmt(deny):<18} {fmt(zdr):<18}")
        # Show error details for failures
        for label in ("data_collection=deny", "zdr=true"):
            status, detail = results[label]
            if status != "ok" and status != "no_endpoints":
                print(f"  └─ {label}: {status}: {detail}")


if __name__ == "__main__":
    main()
