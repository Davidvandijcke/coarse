"""Tests for cli.py — Typer CLI commands."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from coarse.cli import app
from coarse.config import CoarseConfig
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, Review


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

runner = CliRunner()


def _make_review() -> Review:
    return Review(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="03/03/2026",
        overall_feedback=OverviewFeedback(
            issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}.") for i in range(1, 5)]
        ),
        detailed_comments=[
            DetailedComment(number=1, title="Comment 1", quote="Some quote.", feedback="Feedback.")
        ],
    )


def _fake_review_paper(**kwargs):
    """Stub for pipeline.review_paper that returns (Review, markdown)."""
    return _make_review(), "# Test Paper\n"


# ---------------------------------------------------------------------------
# test_review_command_invokes_pipeline
# ---------------------------------------------------------------------------

def test_review_command_invokes_pipeline(tmp_path):
    """review command calls pipeline.review_paper and writes output file."""
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    captured: dict = {}

    def fake_review_paper(pdf_path, model=None, vision=False, skip_cost_gate=False, config=None):
        captured["pdf_path"] = pdf_path
        return _make_review(), "# Test Paper\n"

    with (
        patch("coarse.cli.resolve_api_key", return_value="sk-test"),
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
        patch("coarse.pipeline.review_paper", fake_review_paper),
    ):
        result = runner.invoke(app, ["review", str(pdf), "--yes"])

    assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# test_review_command_default_output_path
# ---------------------------------------------------------------------------

def test_review_command_default_output_path(tmp_path):
    """Output file defaults to <pdf_stem>_review.md in cwd."""
    pdf = tmp_path / "myresearch.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    def fake_review_paper(pdf_path, model=None, vision=False, skip_cost_gate=False, config=None):
        return _make_review(), "# Test Paper\n"

    with (
        patch("coarse.cli.resolve_api_key", return_value="sk-test"),
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
        patch("coarse.pipeline.review_paper", fake_review_paper),
    ):
        result = runner.invoke(app, ["review", str(pdf), "--yes"])

    assert result.exit_code == 0, result.output
    expected = Path("myresearch_review.md")
    assert expected.exists()
    expected.unlink()


# ---------------------------------------------------------------------------
# test_review_command_custom_output_path
# ---------------------------------------------------------------------------

def test_review_command_custom_output_path(tmp_path):
    """--output writes to specified path."""
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    out = tmp_path / "out.md"

    def fake_review_paper(pdf_path, model=None, vision=False, skip_cost_gate=False, config=None):
        return _make_review(), "# Custom Output\n"

    with (
        patch("coarse.cli.resolve_api_key", return_value="sk-test"),
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
        patch("coarse.pipeline.review_paper", fake_review_paper),
    ):
        result = runner.invoke(app, ["review", str(pdf), "--output", str(out), "--yes"])

    assert result.exit_code == 0, result.output
    assert out.exists()
    assert out.read_text() == "# Custom Output\n"


# ---------------------------------------------------------------------------
# test_review_yes_flag_skips_cost_gate
# ---------------------------------------------------------------------------

def test_review_yes_flag_skips_cost_gate(tmp_path):
    """--yes passes skip_cost_gate=True to review_paper."""
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    captured: dict = {}

    def fake_review_paper(pdf_path, model=None, vision=False, skip_cost_gate=False, config=None):
        captured["skip_cost_gate"] = skip_cost_gate
        return _make_review(), "# Test\n"

    with (
        patch("coarse.cli.resolve_api_key", return_value="sk-test"),
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
        patch("coarse.pipeline.review_paper", fake_review_paper),
    ):
        result = runner.invoke(app, ["review", str(pdf), "--yes"])

    assert result.exit_code == 0, result.output
    assert captured.get("skip_cost_gate") is True


# ---------------------------------------------------------------------------
# test_review_missing_api_key_triggers_setup
# ---------------------------------------------------------------------------

def test_review_missing_api_key_triggers_setup(tmp_path, monkeypatch):
    """When no API key found and not a TTY, exit with code 1 and clear error."""
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr("sys.stdin", MagicMock(isatty=lambda: False))

    with (
        patch("coarse.cli.resolve_api_key", return_value=None),
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
    ):
        result = runner.invoke(app, ["review", str(pdf), "--yes"])

    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# test_setup_command_writes_config
# ---------------------------------------------------------------------------

def test_setup_command_writes_config(tmp_path, monkeypatch):
    """setup command saves config with user-provided values."""
    saved: list[CoarseConfig] = []

    def fake_save_config(cfg):
        saved.append(cfg)

    with (
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
        patch("coarse.cli.save_config", fake_save_config),
    ):
        # Provide: default model, then blank for all API key prompts
        from coarse.config import PROVIDER_ENV_VARS

        inputs = ["openai/gpt-4o"] + [""] * len(PROVIDER_ENV_VARS)
        result = runner.invoke(app, ["setup"], input="\n".join(inputs) + "\n")

    assert result.exit_code == 0, result.output
    assert len(saved) == 1
    assert saved[0].default_model == "openai/gpt-4o"


# ---------------------------------------------------------------------------
# test_setup_skips_keys_already_in_env
# ---------------------------------------------------------------------------

def test_setup_skips_keys_already_in_env(tmp_path, monkeypatch):
    """setup skips prompting for keys already set in environment."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-already-set")
    monkeypatch.setattr("sys.stdin", MagicMock(isatty=lambda: True))

    prompts_asked: list[str] = []

    original_prompt = __import__("typer").prompt

    def fake_prompt(text, **kwargs):
        prompts_asked.append(text)
        return kwargs.get("default", "")

    saved: list[CoarseConfig] = []

    def fake_save_config(cfg):
        saved.append(cfg)

    with (
        patch("coarse.cli.load_config", return_value=CoarseConfig()),
        patch("coarse.cli.save_config", fake_save_config),
        patch("typer.prompt", fake_prompt),
    ):
        result = runner.invoke(app, ["setup"])

    # OPENAI_API_KEY is set, so no prompt for it should appear
    assert not any("OPENAI_API_KEY" in p for p in prompts_asked)


# ---------------------------------------------------------------------------
# test_main_module_entrypoint
# ---------------------------------------------------------------------------

def test_main_module_entrypoint():
    """--help via app() works (smoke test for __main__ entry point)."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "coarse" in result.output.lower() or "review" in result.output.lower()


# ---------------------------------------------------------------------------
# test_init_exports
# ---------------------------------------------------------------------------

def test_init_exports():
    """coarse package exports review_paper callable and __version__ == '0.1.0'."""
    import coarse

    assert callable(coarse.review_paper)
    assert coarse.__version__ == "0.1.0"


# ---------------------------------------------------------------------------
# test_review_nonexistent_pdf
# ---------------------------------------------------------------------------

def test_review_nonexistent_pdf():
    """Invoking review with a nonexistent PDF exits with non-zero code."""
    result = runner.invoke(app, ["review", "/nonexistent/path/paper.pdf"])
    assert result.exit_code != 0
