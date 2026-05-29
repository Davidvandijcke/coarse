"""Model manifest — single source of truth for all model selections.

ALL model IDs live here. Never hardcode model strings elsewhere — import from
this module. Verify IDs against OpenRouter before changing:
    python3 ~/.claude/skills/latest-models/scripts/fetch_models.py --search=<model>

Last verified: 2026-03-04
"""

import re

# Primary review model (routed via OpenRouter for non-direct providers)
DEFAULT_MODEL = "qwen/qwen3.5-plus-02-15"

# Secondary reasoning model; carries its own litellm cost entry.
KIMI_K2_5_MODEL = "moonshotai/kimi-k2.5"

# Vision model for post-extraction QA (multimodal, spot-checks Docling output)
# litellm uses 'gemini/' prefix for Google AI Studio (not 'google/')
VISION_MODEL = "gemini/gemini-3-flash-preview"

# Per-provider cheap alternatives (used by --cheap flag)
CHEAP_MODELS: dict[str, str] = {
    "OPENROUTER_API_KEY": "openrouter/google/gemini-3-flash-preview",
    "OPENAI_API_KEY": "openai/gpt-5.1-codex-mini",
    "ANTHROPIC_API_KEY": "anthropic/claude-haiku-4.5",
    "GOOGLE_API_KEY": "google/gemini-3-flash-preview",
    "GROQ_API_KEY": "groq/llama-3.3-70b-versatile",
}

# OCR model for PDF text extraction (Mistral OCR via litellm)
OCR_MODEL = "mistral/mistral-ocr-latest"

# Model used by OpenRouter extraction fallback (google/ prefix for OpenRouter API)
OPENROUTER_EXTRACTION_MODEL = "google/gemini-3-flash-preview"

# Model used for quality evaluation (dev-only, single-judge or panel)
# litellm uses gemini/ prefix for Google AI Studio (not google/ which is Vertex AI)
QUALITY_MODEL = "gemini/gemini-3-flash-preview"

# Literature search via Perplexity Sonar Pro (web-grounded, returns citations)
LITERATURE_SEARCH_MODEL = "perplexity/sonar-pro-search"

# Default host-specific model IDs for the headless CLI backends
# (``coarse-review --host claude|codex|gemini``). These are NOT litellm
# model strings — each value is the bare model ID that the corresponding
# headless CLI (``claude -p``, ``codex exec``, ``gemini -p``) accepts on
# its own command line. Kept here so ``cli_review``, ``headless_review``,
# and ``headless_clients`` all agree on the canonical default.
HEADLESS_DEFAULT_MODELS: dict[str, str] = {
    "claude": "claude-opus-4-6",
    "codex": "gpt-5.4",
    "gemini": "gemini-3.1-pro-preview",
}

# Recall evaluation judge (cheap model for YES/NO semantic matching)
RECALL_JUDGE_MODEL = QUALITY_MODEL

# Model families that need JSON mode instead of tool-calling
JSON_MODE_PREFIXES = ("qwen", "deepseek", "mistral", "together", "gemini")

# Model families that need markdown-JSON mode (instructor MD_JSON)
# These models struggle with both tool-calling and raw JSON but handle
# markdown-wrapped JSON well.  Also need temperature ≤ 0.1 and higher max_tokens.
MARKDOWN_JSON_PREFIXES = ("moonshotai", "kimi")


# ---------------------------------------------------------------------------
# Reasoning-model detection
# ---------------------------------------------------------------------------
#
# Reasoning models (OpenAI o-series + GPT-5 Pro, DeepSeek R1, xAI Grok 4,
# Qwen/Kimi/Claude "thinking" variants, etc.) spend an unbounded portion of
# their max_tokens budget on hidden reasoning before emitting visible output.
# A nominal 4-8k budget gets entirely consumed by internal thinking on hard
# papers, leaving the structured-output response truncated and instructor
# raising IncompleteOutputException.
#
# Callers that route through these models need:
#   1. A much larger max_tokens ceiling (see REASONING_MAX_TOKENS_MULTIPLIER)
#   2. reasoning_effort passed through to cap the thinking budget server-side
#      on providers that accept it (OpenAI o-series + GPT-5 family)
#   3. A cost estimate that includes the reasoning overhead so the pre-flight
#      gate doesn't under-quote by 5-10x
#
# Provider prefixes verified against OpenRouter on 2026-04-11.
REASONING_MODEL_PREFIXES: tuple[str, ...] = (
    # OpenAI o-series — always reasoning
    "openai/o1",
    "openai/o3",
    "openai/o4",
    # OpenAI GPT-5 family — the entire family runs hidden reasoning EXCEPT
    # the `-chat` variants (gpt-5-chat, gpt-5.1-chat, …), which are carved
    # out by _NON_REASONING_SUBSTRINGS below. Verified against OpenRouter
    # /api/v1/models on 2026-05-29. The `openai/gpt-5` prefix covers gpt-5,
    # -mini, -nano, -codex(/-max/-mini), .1/.2/.3/.4/.5, and all -pro; the
    # bare `gpt-5` covers direct-OpenAI-SDK IDs (gpt-5.4, gpt-5-mini, …).
    "openai/gpt-5",
    "gpt-5",
    # DeepSeek R-series (R1 and distills)
    "deepseek/deepseek-r",
    # xAI Grok 4 family — reasoning on by default. Grok 3 mini is also a
    # reasoning model; the non-mini Grok 3 is NOT.
    "x-ai/grok-4",
    "x-ai/grok-3-mini",
    # Perplexity reasoning
    "perplexity/sonar-reasoning",
    # Arcee
    "arcee-ai/maestro-reasoning",
)

# Substrings that indicate a reasoning/thinking variant regardless of provider.
# Matches qwen/*-thinking, moonshotai/kimi-k2-thinking, baidu/ernie-*-thinking,
# anthropic/claude-3.7-sonnet:thinking, perplexity/sonar-reasoning-pro,
# openai/o3-deep-research, openai/o4-mini-deep-research, etc.
REASONING_MODEL_SUBSTRINGS: tuple[str, ...] = (
    "thinking",
    "reasoning",
    "deep-research",
)

# GPT-5-family variants that do NOT run reasoning, overriding the broad
# `gpt-5` prefix above. Only the `-chat` variants (openai/gpt-5-chat,
# gpt-5.1-chat, …) report `reasoning` unsupported on OpenRouter (verified
# 2026-05-29); every other gpt-5* reasons. Checked before the prefix loop in
# is_reasoning_model().
_NON_REASONING_SUBSTRINGS: tuple[str, ...] = ("-chat",)

# Multiplier applied to the caller's requested max_tokens for reasoning
# models. The caller's value is the intended *visible* output budget; the
# multiplier reserves headroom for the hidden reasoning phase.
#
# Calibration: the GPT-5.4 Pro review that triggered this fix used ~15k
# reasoning tokens just in the overview stage (see review 3ee351e6). An 8x
# multiplier on the typical 8k overview budget gives 64k, which covers that
# case with slack. The real model_max ceiling in _clamp_max_tokens will
# still cap to what the model actually supports.
#
# Note: this is the *request budget* multiplier. The cost-estimate overhead
# multiplier is 4x and lives in `llm.py::_REASONING_OVERHEAD_MULTIPLIER` —
# they're intentionally asymmetric because reasoning_effort="medium" is
# expected to cap actual usage well below the raised ceiling. If you change
# one, check the other.
REASONING_MAX_TOKENS_MULTIPLIER: int = 8

# Default reasoning effort passed to litellm's unified `reasoning_effort`
# param on providers that accept it (OpenAI o-series + GPT-5 family). "medium"
# preserves most of the quality advantage of reasoning models while
# preventing the runaway case where the model spends its entire budget on
# reasoning and never emits output. Callers can override by passing
# reasoning_effort explicitly in kwargs.
REASONING_EFFORT_DEFAULT: str = "medium"

_MODEL_FILENAME_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def is_reasoning_model(model_id: str) -> bool:
    """Return True if the model uses hidden reasoning tokens that count
    against max_tokens before any visible output is emitted.

    Use this to decide whether the caller needs to reserve extra
    max_tokens headroom (see REASONING_MAX_TOKENS_MULTIPLIER) and whether
    to pass reasoning_effort through to the provider.
    """
    lower = model_id.lower().removeprefix("openrouter/")
    if any(substring in lower for substring in _NON_REASONING_SUBSTRINGS):
        return False
    for prefix in REASONING_MODEL_PREFIXES:
        if lower.startswith(prefix):
            return True
    return any(substring in lower for substring in REASONING_MODEL_SUBSTRINGS)


def model_filename_slug(model_id: str) -> str:
    """Return a filesystem-friendly slug for a model identifier."""
    slug = _MODEL_FILENAME_SLUG_RE.sub("_", model_id.strip())
    slug = slug.strip("._")
    return slug or "model"


# ---------------------------------------------------------------------------
# Temperature-support detection
# ---------------------------------------------------------------------------
#
# Some models' providers reject the ``temperature`` parameter outright and
# return HTTP 400. Anthropic's Claude Opus 4.7 is the first such model in
# this codebase: it's a reasoning-first release that dropped the
# temperature knob, and both the direct Anthropic API and OpenRouter's
# Anthropic route 400 on any request that carries one (issue #162).
#
# ``litellm.drop_params=True`` can't catch this because litellm's
# per-provider "supported_openai_params" table is indexed on provider
# family (Anthropic), not on specific model IDs — the Anthropic family
# still lists temperature as supported, so the drop gate never fires for
# 4.7. Verified against OpenRouter /api/v1/models on 2026-04-19:
#
#     curl -s https://openrouter.ai/api/v1/models \
#       | jq '.data[] | select(.id=="anthropic/claude-opus-4.7") | .supported_parameters'
#
# returns ['include_reasoning', 'max_tokens', 'reasoning', 'response_format',
# 'stop', 'structured_outputs', 'tool_choice', 'tools', 'verbosity'] — no
# temperature. The matching 4.6 entry does list it.
#
# The same backend ships under two ID conventions depending on the route:
# OpenRouter uses dots (``anthropic/claude-opus-4.7``), while litellm's
# direct-Anthropic and Vertex routes use hyphens
# (``anthropic/claude-opus-4-7``, ``vertex_ai/claude-opus-4-7``, bare
# ``claude-opus-4-7``). Both hit the same model, so both forms must be
# listed — the v1.4.0 fix for #162 only registered the dot form, which
# let ``--model anthropic/claude-opus-4-7`` slip past the gate and 400.
#
# Keep this tuple tight — only add a model once a passed-temperature
# request is confirmed to fail.
TEMPERATURE_UNSUPPORTED_PREFIXES: tuple[str, ...] = (
    # Opus 4.7 (reasoning-first, issue #162): dot / hyphen / Vertex / bare.
    "anthropic/claude-opus-4.7",  # OpenRouter form
    "anthropic/claude-opus-4-7",  # litellm direct-Anthropic form
    "vertex_ai/claude-opus-4-7",  # Vertex AI form
    "claude-opus-4-7",  # bare Anthropic SDK / Bedrock-style ID
    # Opus 4.8 — same reasoning-first behavior; verified temperature
    # unsupported on OpenRouter 2026-05-28. The dot prefix also covers
    # the ``-fast`` variant via startswith.
    "anthropic/claude-opus-4.8",  # OpenRouter form (covers -fast)
    "anthropic/claude-opus-4-8",  # litellm direct-Anthropic form
    "vertex_ai/claude-opus-4-8",  # Vertex AI form
    "claude-opus-4-8",  # bare Anthropic SDK / Bedrock-style ID
    # GPT-5 family rejects temperature on the OpenRouter route (verified
    # OpenRouter /api/v1/models 2026-05-29 — the whole family, not just 5.5).
    # litellm's OpenAI param table is no more trustworthy per-model than the
    # Anthropic one, so gate the family by prefix. `openai/gpt-5` covers the
    # dot / codex / pro / chat variants; bare `gpt-5` covers direct-OpenAI-SDK
    # IDs. (gpt-5-image* technically accept temperature, but coarse never
    # routes a review to an image model.) Omitting temperature is harmless on
    # routes that accept it; it only prevents a 400 on routes that don't.
    "openai/gpt-5",  # OpenRouter / litellm OpenAI form (covers all gpt-5*)
    "gpt-5",  # bare OpenAI SDK ID
)


def supports_temperature(model_id: str) -> bool:
    """Return False if the provider rejects the ``temperature`` parameter
    for this model.

    Strips an optional ``openrouter/`` prefix so direct-provider and
    OpenRouter-routed variants of the same model resolve the same way.
    """
    lower = model_id.lower().removeprefix("openrouter/")
    return not any(lower.startswith(prefix) for prefix in TEMPERATURE_UNSUPPORTED_PREFIXES)
