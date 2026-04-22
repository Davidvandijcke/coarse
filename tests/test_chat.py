"""Tests for ChatSession (chat-mode logic, no CLI)."""

from __future__ import annotations

from pathlib import Path

import pytest

from coarse.chat import ChatSession


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


def test_chatsession_loads_paper_and_review(fake_paper: Path, fake_review: Path) -> None:
    session = ChatSession(paper_path=fake_paper, review_path=fake_review, model="openai/gpt-4o-mini")
    assert "studies X" in session.paper_text
    assert "The paper is about X" in session.review_text
