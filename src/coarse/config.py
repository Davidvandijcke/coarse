"""Config management for coarse.

Reads/writes ~/.coarse/config.toml. API key resolution checks env vars first,
then the config file. Note: litellm has its own env-var-based key resolution at
call time; resolve_api_key() is for pre-flight checks and CLI prompting only.
"""

from __future__ import annotations

import logging
import os
import tomllib
from pathlib import Path

import tomli_w
from pydantic import BaseModel, Field

from coarse.models import DEFAULT_MODEL, VISION_MODEL

logger = logging.getLogger(__name__)

# Maps provider name -> environment variable name.
# Extensible: add entries as more providers are supported.
# Note: "mistral" is kept here for users who want to call Mistral chat models
# directly (e.g. `coarse review --model mistral/mistral-large`). Mistral OCR
# (for PDF extraction) is NOT routed through this — it always goes through
# OpenRouter's file-parser plugin; see src/coarse/extraction.py.
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
    default_model: str = DEFAULT_MODEL
    vision_model: str = VISION_MODEL
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

    # Warn if config file containing API keys is readable by others
    try:
        mode = path.stat().st_mode
        if mode & 0o077:  # group or world readable/writable
            logger.warning(
                "Config file %s has insecure permissions (%o). Run: chmod 600 %s",
                path,
                mode & 0o777,
                path,
            )
    except OSError:
        pass

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return CoarseConfig.model_validate(data)
    except Exception:
        logger.warning("Failed to parse %s, using defaults", path, exc_info=True)
        return CoarseConfig()


def save_config(config: CoarseConfig) -> None:
    """Serialize config to ~/.coarse/config.toml, creating the directory if needed."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = config.model_dump()
    # Strip None api_key values
    data["api_keys"] = {k: v for k, v in data["api_keys"].items() if v is not None}
    with open(path, "wb") as f:
        f.write(tomli_w.dumps(data).encode())
    # Restrict permissions: only owner can read/write API keys
    path.chmod(0o600)
    path.parent.chmod(0o700)


def _normalize_provider(provider: str) -> str:
    """Normalize a litellm model string or provider name to a bare provider name.

    Examples:
        'openai/gpt-4o' -> 'openai'
        'anthropic'     -> 'anthropic'
    """
    return provider.split("/")[0].strip().lower()


def _clean_env(name: str) -> str | None:
    """Read an env var and return its stripped value, or None if unset/blank.

    Whitespace-only values are treated as unset — they're otherwise truthy in
    plain `if os.environ.get(...)` checks but produce an empty `Authorization:
    Bearer ` header downstream, which OpenRouter rejects with 401 "Missing
    Authentication header".
    """
    value = (os.environ.get(name) or "").strip()
    return value or None


def resolve_api_key(provider: str, config: CoarseConfig | None = None) -> str | None:
    """Return API key for provider; env vars take priority over config file.

    Args:
        provider: Provider name or litellm model string (e.g. 'openai' or 'openai/gpt-4o').
        config: Optional pre-loaded config; if None, load_config() is called.

    Returns:
        API key string, or None if not found. Whitespace-only values are
        treated as absent.
    """
    name = _normalize_provider(provider)

    # Check environment variable first
    env_var = PROVIDER_ENV_VARS.get(name)
    if env_var:
        value = _clean_env(env_var)
        if value:
            return value

    # litellm's gemini/ prefix uses GEMINI_API_KEY, but users often set GOOGLE_API_KEY
    if name == "gemini":
        google_key = _clean_env("GOOGLE_API_KEY")
        if google_key:
            return google_key

    # Fall back to config file
    if config is None:
        config = load_config()
    cfg_key = (config.api_keys.get(name) or "").strip()
    if cfg_key:
        return cfg_key

    # Last resort: OpenRouter can proxy most providers
    or_key = _clean_env("OPENROUTER_API_KEY")
    if or_key:
        return or_key

    return None
