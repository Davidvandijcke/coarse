"""Tests for ChatSession (chat-mode logic, no CLI)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_chatsession_builds_system_prompt(fake_paper: Path, fake_review: Path) -> None:
    session = ChatSession(paper_path=fake_paper, review_path=fake_review, model="openai/gpt-4o-mini")
    sys_prompt = session.system_prompt()
    # Persona markers
    assert "peer reviewer" in sys_prompt.lower()
    # Literature-search sentinel must be documented
    assert "<<SEARCH:" in sys_prompt
    # Tone block fragment from coarse.prompts._TONE_BLOCK
    assert "constructive but direct colleague" in sys_prompt


def test_chatsession_initial_user_message_includes_paper_and_review(
    fake_paper: Path, fake_review: Path
) -> None:
    session = ChatSession(paper_path=fake_paper, review_path=fake_review, model="openai/gpt-4o-mini")
    initial = session.initial_user_message()
    assert "studies X" in initial          # paper body
    assert "The paper is about X" in initial  # review body


def test_ask_returns_model_reply(fake_paper: Path, fake_review: Path) -> None:
    session = ChatSession(paper_path=fake_paper, review_path=fake_review, model="openai/gpt-4o-mini")

    fake_client = MagicMock()
    fake_client.complete_text.return_value = "Hello, author."

    with patch("coarse.chat.LLMClient", return_value=fake_client):
        reply = session.ask("What did you mean by section 3?")

    assert reply == "Hello, author."
    # Subsequent turns should reuse history — the message list grows.
    assert len(session.history) >= 2  # initial user + assistant + new user + assistant


def test_ask_intercepts_search_sentinel(fake_paper: Path, fake_review: Path) -> None:
    """Model emits <<SEARCH: q>>, harness calls literature search, re-prompts."""
    session = ChatSession(paper_path=fake_paper, review_path=fake_review, model="openai/gpt-4o-mini")

    main_client = MagicMock()
    # First call: model asks for a search. Second call: model gives the final answer.
    main_client.complete_text.side_effect = [
        "I should look this up.\n<<SEARCH: weighted Cohen's d for survey data>>",
        "Based on the literature, here is the answer.",
    ]

    lit_client = MagicMock()
    lit_client.complete_text.return_value = "MOCK_LIT_RESULTS"

    def client_factory(model: str | None = None):
        # First instantiation in ask() -> main client.
        # Second instantiation (for literature search) -> lit client.
        if model and "perplexity" in (model or "").lower():
            return lit_client
        return main_client

    with patch("coarse.chat.LLMClient", side_effect=client_factory):
        reply = session.ask("Why not a t-test?")

    assert reply == "Based on the literature, here is the answer."
    # Search was actually invoked
    lit_client.complete_text.assert_called_once()
    lit_call_args = lit_client.complete_text.call_args
    lit_messages = lit_call_args.args[0] if lit_call_args.args else lit_call_args.kwargs["messages"]
    assert any("weighted Cohen's d for survey data" in m["content"] for m in lit_messages)
    # Search results were folded back into the main conversation
    assert any("MOCK_LIT_RESULTS" in m["content"] for m in session.history if m["role"] == "user")
