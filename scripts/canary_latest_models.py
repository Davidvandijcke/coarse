"""Bounded live compatibility checks using Coarse's production LLM client.

Run with OPENROUTER_API_KEY. Reserves worst-case token cost before every
attempt; reservations are never refunded, even on transport failure.
"""

import json
import os
from pathlib import Path

import litellm

from coarse.config import CoarseConfig
from coarse.llm import LLMClient
from coarse.models import (
    CLAUDE_FABLE_5_1_MODEL,
    GEMINI_3_8_FLASH_MODEL,
    GPT_6_ASTRA_MODEL,
    GPT_6_ASTRA_PRO_MODEL,
    QWEN_3_8_MAX_MODEL,
)
from coarse.prompts import METADATA_SYSTEM, metadata_user
from coarse.types import OverviewFeedback, PaperMetadata

MODELS = (
    GPT_6_ASTRA_MODEL,
    GPT_6_ASTRA_PRO_MODEL,
    CLAUDE_FABLE_5_1_MODEL,
    GEMINI_3_8_FLASH_MODEL,
    QWEN_3_8_MAX_MODEL,
)
PAPER = (
    "# Randomized Tutoring and Test Scores\nWe randomly assigned 100 students "
    "to tutoring and 100 to control. Mean scores were 80 and 75. "
    "We conclude tutoring increases scores by five points. We report no "
    "standard errors, confidence intervals, attrition, or baseline balance."
)


def main():
    import urllib.request

    catalog = {
        m["id"]: m
        for m in json.load(urllib.request.urlopen("https://openrouter.ai/api/v1/models"))["data"]
    }
    output = Path(os.environ.get("CANARY_OUTPUT", "/tmp/coarse-model-canaries.json"))
    ledger = {"limit_usd": 2.0, "reserved_usd": 0.0, "calls": [], "results": []}
    if output.exists():
        raise RuntimeError("Use a fresh ledger; never overwrite prior spend evidence")
    original = litellm.completion

    def save():
        output.write_text(json.dumps(ledger, indent=2, default=str) + "\n")

    def guarded(*args, **kwargs):
        model = kwargs["model"].removeprefix("openrouter/")
        assert model in MODELS
        assert not kwargs.get("tools") and not kwargs.get("plugins")
        # Bound hidden reasoning plus visible output, disable transport retries.
        kwargs["max_tokens"] = min(kwargs["max_tokens"], 2048)
        kwargs["num_retries"] = 0
        pricing = catalog[model]["pricing"]
        # UTF-8 bytes upper-bound ordinary text tokens. Include a generous
        # envelope/schema allowance; Instructor has already expanded messages.
        tokens_in = len(json.dumps(kwargs["messages"]).encode()) + 4096
        reservation = tokens_in * max(
            float(pricing["prompt"]), float(pricing.get("input_cache_write", 0))
        ) + kwargs["max_tokens"] * float(pricing["completion"])
        if ledger["reserved_usd"] + reservation > ledger["limit_usd"]:
            raise RuntimeError("Canary reservation budget exhausted")
        ledger["reserved_usd"] += reservation
        row = {"model": model, "reserved_usd": reservation, "max_tokens": kwargs["max_tokens"]}
        ledger["calls"].append(row)
        save()
        try:
            response = original(*args, **kwargs)
            row["usage"] = response.usage.model_dump()
            row["id"] = response.id
            row["finish_reason"] = response.choices[0].finish_reason
            return response
        except Exception as exc:
            row["error_type"] = type(exc).__name__
            raise
        finally:
            save()

    litellm.completion = guarded
    for model in MODELS:
        client = LLMClient("openrouter/" + model, CoarseConfig())
        tasks = [
            (
                "metadata",
                PaperMetadata,
                [
                    {"role": "system", "content": METADATA_SYSTEM},
                    {
                        "role": "user",
                        "content": metadata_user(PAPER, "", "Randomized Tutoring and Test Scores"),
                    },
                ],
            ),
            (
                "overview",
                OverviewFeedback,
                [
                    {
                        "role": "system",
                        "content": (
                            "Review the supplied short research manuscript. "
                            "Identify one substantive methodological issue grounded in the text. "
                            "Be concise."
                        ),
                    },
                    {"role": "user", "content": PAPER},
                ],
            ),
        ]
        for stage, schema, messages in tasks:
            row = {"model": model, "stage": stage}
            try:
                result = client.complete(
                    messages, schema, max_tokens=512, reasoning_effort="low", timeout=90
                )
                if stage == "metadata":
                    assert result.title == "Randomized Tutoring and Test Scores"
                else:
                    assert result.issues and result.issues[0].body
                row.update(status="passed", output=result.model_dump())
            except Exception as exc:
                row.update(status="failed", error_type=type(exc).__name__)
            ledger["results"].append(row)
            save()
            print(model, stage, row["status"], flush=True)
    print("Reserved USD:", ledger["reserved_usd"], flush=True)
    if any(r["status"] != "passed" for r in ledger["results"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
