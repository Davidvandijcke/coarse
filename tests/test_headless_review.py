from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from coarse.headless_review import _find_openrouter_key, _make_client_factory, main
from coarse.models import HEADLESS_DEFAULT_MODELS, model_filename_slug


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
    """Regression: pipeline.py calls `LLMClient(model=..., config=...)` at
    several sites (extraction QA, main review client, vision QA). The
    monkey-patch in `_patch_llmclient` replaces LLMClient with the factory
    returned by `_make_client_factory`, so the factory must accept any
    shape of call the pipeline would make against the real LLMClient,
    including positional/keyword `model` and `config`, and silently drop
    the extras (the headless client uses the closure-captured values).

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


def test_main_writes_review_filename_with_default_model_slug(tmp_path, capsys) -> None:
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"%PDF-1.4 fake")
    out_dir = tmp_path / "out"

    review = SimpleNamespace(detailed_comments=[])

    expected = out_dir / f"paper_review_{model_filename_slug(HEADLESS_DEFAULT_MODELS['codex'])}.md"

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
