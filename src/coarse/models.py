"""Model manifest — single source of truth for all model selections."""

# Primary review model (routed via OpenRouter for non-direct providers)
DEFAULT_MODEL = "qwen/qwen3.5-plus-02-15"

# Vision model for post-extraction QA (multimodal, spot-checks Docling output)
VISION_MODEL = "gemini/gemini-3-flash"

# Per-provider cheap alternatives (used by --cheap flag)
CHEAP_MODELS: dict[str, str] = {
    "OPENROUTER_API_KEY": "openrouter/google/gemini-3-flash",
    "OPENAI_API_KEY": "openai/gpt-4o-mini",
    "ANTHROPIC_API_KEY": "anthropic/claude-4.5-haiku",
    "GOOGLE_API_KEY": "google/gemini-3-flash",
    "GROQ_API_KEY": "groq/llama-3.3-70b-versatile",
}

# Model families that need JSON mode instead of tool-calling
JSON_MODE_PREFIXES = ("qwen", "deepseek", "mistral", "together", "gemini")
