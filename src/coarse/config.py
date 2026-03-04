"""Config management for coarse.

Reads/writes ~/.coarse/config.toml. API key resolution checks env vars first,
then the config file. Note: litellm has its own env-var-based key resolution at
call time; resolve_api_key() is for pre-flight checks and CLI prompting only.
"""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

import tomli_w
from pydantic import BaseModel, Field

# Maps provider name -> environment variable name.
# Extensible: add entries as more providers are supported.
PROVIDER_ENV_VARS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "cohere": "COHERE_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "groq": "GROQ_API_KEY",
    "together": "TOGETHER_API_KEY",
    "azure": "AZURE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


class CoarseConfig(BaseModel):
    default_model: str = "qwen/qwen3.5-plus-02-15"
    vision_model: str = "gemini/gemini-3-flash"
    extraction_qa: bool = True
    max_cost_usd: float = 10.0
    api_keys: dict[str, str] = Field(default_factory=dict)


def get_config_path() -> Path:
    """Single source of truth for config file location."""
    return Path("~/.coarse/config.toml").expanduser()


def load_config() -> CoarseConfig:
    """Load config from ~/.coarse/config.toml, falling back to defaults."""
    path = get_config_path()
    if not path.exists():
        return CoarseConfig()
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return CoarseConfig.model_validate(data)


def save_config(config: CoarseConfig) -> None:
    """Serialize config to ~/.coarse/config.toml, creating the directory if needed."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = config.model_dump()
    # Strip None api_key values
    data["api_keys"] = {k: v for k, v in data["api_keys"].items() if v is not None}
    with open(path, "wb") as f:
        f.write(tomli_w.dumps(data).encode())


def _normalize_provider(provider: str) -> str:
    """Normalize a litellm model string or provider name to a bare provider name.

    Examples:
        'openai/gpt-4o' -> 'openai'
        'anthropic'     -> 'anthropic'
    """
    return provider.split("/")[0].strip().lower()


def resolve_api_key(provider: str, config: CoarseConfig | None = None) -> str | None:
    """Return API key for provider; env vars take priority over config file.

    Args:
        provider: Provider name or litellm model string (e.g. 'openai' or 'openai/gpt-4o').
        config: Optional pre-loaded config; if None, load_config() is called.

    Returns:
        API key string, or None if not found.
    """
    name = _normalize_provider(provider)

    # Check environment variable first
    env_var = PROVIDER_ENV_VARS.get(name)
    if env_var:
        value = os.environ.get(env_var)
        if value:
            return value

    # For unknown providers (e.g. qwen/, deepseek/), fall back to OpenRouter key
    if name not in PROVIDER_ENV_VARS:
        or_key = os.environ.get("OPENROUTER_API_KEY")
        if or_key:
            return or_key

    # Fall back to config file
    if config is None:
        config = load_config()
    return config.api_keys.get(name) or None
