from __future__ import annotations

from coarse.headless_review import _find_openrouter_key


def test_find_openrouter_key_reads_api_keys_config(tmp_path, monkeypatch) -> None:
    config_dir = tmp_path / ".coarse"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[api_keys]\nopenrouter = "sk-or-v1-config"\n',
        encoding="utf-8",
    )

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    assert _find_openrouter_key() == "sk-or-v1-config"
