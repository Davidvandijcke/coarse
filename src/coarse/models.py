"""Model manifest — single source of truth for all model selections.

ALL model IDs live here. Never hardcode model strings elsewhere — import from
this module. Verify IDs against OpenRouter before changing:
    python3 ~/.claude/skills/latest-models/scripts/fetch_models.py --search=<model>

Last verified: 2026-03-04
"""

# Primary review model (routed via OpenRouter for non-direct providers)
DEFAULT_MODEL = "qwen/qwen3.5-plus-02-15"

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

