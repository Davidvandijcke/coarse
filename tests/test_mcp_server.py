"""Tests for the coarse MCP server."""

from __future__ import annotations

from coarse.mcp_server import mcp, ping


def test_ping_returns_pong() -> None:
    assert ping() == "pong"


def test_server_name_is_coarse_chat() -> None:
    assert mcp.name == "coarse-chat"


from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.mcp_server import _sessions, start_chat


@pytest.fixture(autouse=True)
def _clear_sessions():
    _sessions.clear()
    yield
    _sessions.clear()


@pytest.fixture
def fake_paper(tmp_path: Path) -> Path:
    p = tmp_path / "paper.md"
    p.write_text("# Title\n\nThis paper studies X.\n", encoding="utf-8")
    return p


@pytest.fixture
def fake_review(tmp_path: Path) -> Path:
    r = tmp_path / "review.md"
    r.write_text("## Overview\n\nThe paper is about X.\n", encoding="utf-8")
    return r


def test_start_chat_returns_uuid_string(fake_paper: Path, fake_review: Path) -> None:
    session_id = start_chat(str(fake_paper), str(fake_review))
    assert isinstance(session_id, str)
    assert len(session_id) >= 32  # uuid4 hex is 32+ chars


def test_start_chat_stores_session_in_registry(fake_paper: Path, fake_review: Path) -> None:
    session_id = start_chat(str(fake_paper), str(fake_review))
    assert session_id in _sessions
    assert "studies X" in _sessions[session_id].paper_text


def test_start_chat_passes_model_through(fake_paper: Path, fake_review: Path) -> None:
    session_id = start_chat(str(fake_paper), str(fake_review), model="openai/gpt-4o-mini")
    assert _sessions[session_id].model == "openai/gpt-4o-mini"


def test_start_chat_raises_when_paper_missing(tmp_path: Path, fake_review: Path) -> None:
    missing = tmp_path / "does_not_exist.md"
    with pytest.raises(FileNotFoundError, match="paper"):
        start_chat(str(missing), str(fake_review))


def test_start_chat_raises_when_review_missing(fake_paper: Path, tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.md"
    with pytest.raises(FileNotFoundError, match="review"):
        start_chat(str(fake_paper), str(missing))
