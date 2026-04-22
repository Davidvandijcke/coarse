"""Tests for the `coarse chat` CLI subcommand."""

from __future__ import annotations

from typer.testing import CliRunner

from coarse.cli import app

runner = CliRunner()


def test_chat_subcommand_is_registered() -> None:
    """`coarse chat --help` exits 0 and mentions chat."""
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0, result.output
    assert "chat" in result.output.lower()
