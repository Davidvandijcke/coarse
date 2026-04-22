"""Tests for the `coarse chat` CLI subcommand."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from coarse.cli import app

runner = CliRunner()


def test_chat_subcommand_is_registered() -> None:
    """`coarse chat --help` exits 0 and mentions chat."""
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0, result.output
    assert "chat" in result.output.lower()


def test_chat_repl_runs_one_question_then_quits(tmp_path: Path) -> None:
    paper = tmp_path / "paper.md"
    paper.write_text("# Title\n\nbody\n", encoding="utf-8")
    review = tmp_path / "review.md"
    review.write_text("## Overview\n\nreview body\n", encoding="utf-8")

    fake_session = MagicMock()
    fake_session.ask.return_value = "Reviewer reply."

    with patch("coarse.cli_chat.ChatSession", return_value=fake_session):
        result = runner.invoke(
            app,
            ["chat", str(paper), str(review)],
            input="What did you mean?\n/quit\n",
        )

    assert result.exit_code == 0, result.output
    assert "Reviewer reply." in result.output
    fake_session.ask.assert_called_once_with("What did you mean?")
