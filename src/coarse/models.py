"""Model manifest — single source of truth for all model selections.

ALL model IDs live here. Never hardcode model strings elsewhere — import from
this module. Verify IDs against OpenRouter before changing:
    python3 ~/.claude/skills/latest-models/scripts/fetch_models.py --search=<model>

Last verified: 2026-03-04
"""

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
#      on providers that accept it (OpenAI o-series + GPT-5 Pro)
#   3. A cost estimate that includes the reasoning overhead so the pre-flight
#      gate doesn't under-quote by 5-10x
#
# Provider prefixes verified against OpenRouter on 2026-04-11.
REASONING_MODEL_PREFIXES: tuple[str, ...] = (
    # OpenAI o-series — always reasoning
    "openai/o1",
    "openai/o3",
    "openai/o4",
    # OpenAI GPT-5 "Pro" variants default to high reasoning effort
    "openai/gpt-5-pro",
    "openai/gpt-5.1-pro",
    "openai/gpt-5.2-pro",
    "openai/gpt-5.3-pro",
    "openai/gpt-5.4-pro",
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

# Multiplier applied to the caller's requested max_tokens for reasoning
# models. The caller's value is the intended *visible* output budget; the
# multiplier reserves headroom for the hidden reasoning phase.
#
# Calibration: the GPT-5.4 Pro review that triggered this fix used ~15k
# reasoning tokens just in the overview stage (see review 3ee351e6). An 8x
# multiplier on the typical 8k overview budget gives 64k, which covers that
# case with slack. The real model_max ceiling in _clamp_max_tokens will
# still cap to what the model actually supports.
REASONING_MAX_TOKENS_MULTIPLIER: int = 8

# Default reasoning effort passed to litellm's unified `reasoning_effort`
# param on providers that accept it (OpenAI o-series + GPT-5 Pro). "medium"
# preserves most of the quality advantage of reasoning models while
# preventing the runaway case where the model spends its entire budget on
# reasoning and never emits output. Callers can override by passing
# reasoning_effort explicitly in kwargs.
REASONING_EFFORT_DEFAULT: str = "medium"


def is_reasoning_model(model_id: str) -> bool:
    """Return True if the model uses hidden reasoning tokens that count
    against max_tokens before any visible output is emitted.

    Use this to decide whether the caller needs to reserve extra
    max_tokens headroom (see REASONING_MAX_TOKENS_MULTIPLIER) and whether
    to pass reasoning_effort through to the provider.
    """
    lower = model_id.lower().removeprefix("openrouter/")
    for prefix in REASONING_MODEL_PREFIXES:
        if lower.startswith(prefix):
            return True
    return any(substring in lower for substring in REASONING_MODEL_SUBSTRINGS)
