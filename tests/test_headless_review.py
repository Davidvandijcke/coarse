from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from coarse.headless_review import (
    _find_openrouter_key,
    _force_openrouter_model,
    _looks_like_openrouter_key,
    _make_client_factory,
    main,
    openrouter_key_preflight_error,
)
from coarse.models import (
    LITELLM_OPENROUTER_PREFIX,
    OPENROUTER_EXTRACTION_MODEL,
    VISION_MODEL,
    model_filename_slug,
)


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


def test_client_factory_accepts_pipeline_style_kwargs() -> None:
    """The base headless factory accepts every pipeline constructor shape.

    `_patch_llmclient` wraps this base factory with the explicit-model API
    route tested below. The base still needs to tolerate keyword and legacy
    positional extras when it constructs a headless review client.

    Before this regression test existed, the factory's signature was
    `def _factory(stage: str = "")`, so headless reviews blew up with
    `_factory() got an unexpected keyword argument 'model'` the moment
    the pipeline built its main LLMClient.
    """
    for host, client_attr in (
        ("claude", "ClaudeCodeClient"),
        ("codex", "CodexClient"),
        ("gemini", "GeminiClient"),
    ):
        with patch(f"coarse.headless_clients.{client_attr}") as fake_client:
            factory = _make_client_factory(host, model=None, effort="low")

            # stage-only call (the `ReviewAgent.build_client` path)
            factory(stage="overview")
            # pipeline.py:294 / 326 style call (model + config kwargs)
            factory(model="headless-claude", config=object())
            # positional model (legacy call shape, shouldn't happen but
            # the factory should not be picky)
            factory("overview", "ignored-positional", extra=1)

            assert fake_client.call_count == 3


def test_client_factory_keeps_explicit_stage_model_on_api_route() -> None:
    """Extraction QA must use the real multimodal client, not the text-only host."""
    openrouter_vision_model = LITELLM_OPENROUTER_PREFIX + OPENROUTER_EXTRACTION_MODEL
    for host, client_attr in (
        ("claude", "ClaudeCodeClient"),
        ("codex", "CodexClient"),
        ("gemini", "GeminiClient"),
    ):
        api_client = MagicMock()
        config = object()
        with patch(f"coarse.headless_clients.{client_attr}") as headless_client:
            factory = _make_client_factory(
                host,
                model=None,
                effort="low",
                api_client_factory=api_client,
                api_model_mapper=_force_openrouter_model,
            )

            factory(model=VISION_MODEL, config=config)
            api_client.assert_called_once_with(
                model=openrouter_vision_model,
                config=config,
            )
            headless_client.assert_not_called()

            factory(model=f"headless-{host}", config=config)
            headless_client.assert_called_once()


def test_force_openrouter_model_is_idempotent_and_normalizes_gemini() -> None:
    openrouter_vision_model = LITELLM_OPENROUTER_PREFIX + OPENROUTER_EXTRACTION_MODEL
    assert _force_openrouter_model(VISION_MODEL) == openrouter_vision_model
    assert _force_openrouter_model(OPENROUTER_EXTRACTION_MODEL) == openrouter_vision_model
    assert _force_openrouter_model(openrouter_vision_model) == openrouter_vision_model
    assert _force_openrouter_model("custom-model") == "custom-model"


def test_deep_literature_requires_key_even_for_preextracted_non_pdf(tmp_path, monkeypatch) -> None:
    paper = tmp_path / "paper.md"
    extracted = tmp_path / "paper.extracted.md"
    paper.write_text("# Paper\n", encoding="utf-8")
    extracted.write_text("# Extracted\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with patch("coarse.headless_review._find_openrouter_key", return_value=None):
        assert openrouter_key_preflight_error(paper, extracted) is None
        error = openrouter_key_preflight_error(
            paper,
            extracted,
            deep_literature_search=True,
        )

    assert error is not None
    assert "Deep literature search requires" in error


def test_main_writes_plain_review_filename_without_explicit_model(tmp_path, capsys) -> None:
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"%PDF-1.4 fake")
    out_dir = tmp_path / "out"

    review = SimpleNamespace(detailed_comments=[])

    expected = out_dir / "paper_review.md"

    with (
        patch("coarse.headless_review._require_openrouter_key"),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(review, "# Review\n", object()),
        ),
    ):
        rc = main(["--host", "codex", str(paper), ".", str(out_dir)])

    assert rc == 0
    assert expected.read_text(encoding="utf-8") == "# Review\n"
    assert str(expected) in capsys.readouterr().out


def test_main_writes_model_slug_filename_with_explicit_model(tmp_path, capsys) -> None:
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"%PDF-1.4 fake")
    out_dir = tmp_path / "out"

    review = SimpleNamespace(detailed_comments=[])

    expected = out_dir / f"paper_review_{model_filename_slug('anthropic/claude-sonnet-4-6')}.md"

    with (
        patch("coarse.headless_review._require_openrouter_key"),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(review, "# Review\n", object()),
        ),
    ):
        rc = main(
            [
                "--host",
                "codex",
                "--model",
                "anthropic/claude-sonnet-4-6",
                str(paper),
                ".",
                str(out_dir),
            ]
        )

    assert rc == 0
    assert expected.read_text(encoding="utf-8") == "# Review\n"
    assert str(expected) in capsys.readouterr().out


# --- #197: reject non-key values so junk is never forwarded as a Bearer token


def test_looks_like_openrouter_key_accepts_real_rejects_junk() -> None:
    assert _looks_like_openrouter_key("sk-or-v1-abc123")
    assert _looks_like_openrouter_key("  sk-or-v1-abc123  ")  # surrounding ws ok
    assert not _looks_like_openrouter_key(None)
    assert not _looks_like_openrouter_key("")
    assert not _looks_like_openrouter_key("   ")
    assert not _looks_like_openrouter_key("FROM_ENV")
    assert not _looks_like_openrouter_key("sk-ant-not-openrouter")


def test_find_openrouter_key_rejects_from_env_placeholder_in_config(tmp_path, monkeypatch) -> None:
    """#197: a literal `openrouter = "FROM_ENV"` in config with an empty env var
    must resolve to None — not the literal string, which would be sent as
    `Authorization: Bearer FROM_ENV` and 401 deep in extraction."""
    config_dir = tmp_path / ".coarse"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[api_keys]\nopenrouter = "FROM_ENV"\n', encoding="utf-8"
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)  # ensure no stray ./.env is picked up
    assert _find_openrouter_key() is None


def test_find_openrouter_key_skips_junk_env_and_uses_valid_config(tmp_path, monkeypatch) -> None:
    """#197: a junk env value is skipped so resolution falls through to a valid
    config key instead of short-circuiting on the junk."""
    config_dir = tmp_path / ".coarse"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[api_keys]\nopenrouter = "sk-or-v1-real"\n', encoding="utf-8"
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "FROM_ENV")  # junk, must be ignored
    monkeypatch.chdir(tmp_path)
    assert _find_openrouter_key() == "sk-or-v1-real"
