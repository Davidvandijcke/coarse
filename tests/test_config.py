import os
from pathlib import Path

import pytest
import tomli_w

from coarse.config import (
    CoarseConfig,
    get_config_path,
    load_config,
    resolve_api_key,
    save_config,
)
from coarse.models import (
    DEFAULT_MODEL,
    VISION_MODEL,
)


@pytest.fixture()
def tmp_config_path(tmp_path, monkeypatch):
    """Redirect config path to a temp directory."""
    config_file = tmp_path / ".coarse" / "config.toml"

    def _fake_get_config_path():
        return config_file

    monkeypatch.setattr("coarse.config.get_config_path", _fake_get_config_path)
    return config_file


# --- load_config ---

def test_load_config_missing_file(tmp_config_path):
    cfg = load_config()
    assert isinstance(cfg, CoarseConfig)
    assert cfg.default_model == DEFAULT_MODEL
    assert cfg.vision_model == VISION_MODEL
    assert cfg.extraction_qa is True
    assert cfg.max_cost_usd == 10.0
    assert cfg.api_keys == {}


def test_load_config_partial_toml(tmp_config_path):
    tmp_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_config_path, "wb") as f:
        f.write(tomli_w.dumps({"default_model": "anthropic/claude-3-5-sonnet"}).encode())

    cfg = load_config()
    assert cfg.default_model == "anthropic/claude-3-5-sonnet"
    assert cfg.max_cost_usd == 10.0
    assert cfg.api_keys == {}


# --- save_config + load_config ---

def test_save_and_reload(tmp_config_path):
    original = CoarseConfig(
        default_model="anthropic/claude-3-5-sonnet",
        max_cost_usd=5.0,
        api_keys={"anthropic": "sk-ant-test"},
    )
    save_config(original)
    reloaded = load_config()
    assert reloaded.default_model == original.default_model
    assert reloaded.max_cost_usd == original.max_cost_usd
    assert reloaded.api_keys == original.api_keys


def test_save_config_creates_directory(tmp_path, monkeypatch):
    nested = tmp_path / "a" / "b" / ".coarse" / "config.toml"

    def _fake_get_config_path():
        return nested

    monkeypatch.setattr("coarse.config.get_config_path", _fake_get_config_path)
    assert not nested.parent.exists()
    save_config(CoarseConfig())
    assert nested.exists()


# --- resolve_api_key ---

def test_resolve_api_key_env_var(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-openai")
    result = resolve_api_key("openai", CoarseConfig())
    assert result == "sk-env-openai"


def test_resolve_api_key_config_file(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    cfg = CoarseConfig(api_keys={"anthropic": "sk-ant-from-config"})
    result = resolve_api_key("anthropic", cfg)
    assert result == "sk-ant-from-config"


def test_resolve_api_key_env_priority(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-wins")
    cfg = CoarseConfig(api_keys={"openai": "sk-config-loses"})
    result = resolve_api_key("openai", cfg)
    assert result == "sk-env-wins"


def test_resolve_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = resolve_api_key("openai", CoarseConfig())
    assert result is None


def test_resolve_api_key_openrouter_fallback(monkeypatch):
    """When only OPENROUTER_API_KEY is set, it serves as fallback for any provider."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    result = resolve_api_key("gemini/gemini-3-flash-preview", CoarseConfig())
    assert result == "sk-or-test"


def test_resolve_api_key_model_prefix_stripped(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-openai")
    result = resolve_api_key("openai/gpt-4o", CoarseConfig())
    assert result == "sk-env-openai"


# --- get_config_path ---

def test_get_config_path():
    path = get_config_path()
    assert isinstance(path, Path)
    assert path.parts[-1] == "config.toml"
    assert path.parts[-2] == ".coarse"
    assert str(path).startswith(str(Path.home()))
