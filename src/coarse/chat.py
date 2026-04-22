"""Chat-mode reviewer: interactive Q&A over a paper + prior review.

Stateless from the LLM's perspective on each turn — we resend the full
message history every call. The system prompt names the literature-search
sentinel; the chat loop intercepts it and calls Perplexity. See cli_chat.py
for the REPL wrapper.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from coarse.extraction import extract_file
from coarse.prompts import CHAT_SYSTEM, chat_user_initial


@dataclass
class ChatSession:
    paper_path: Path
    review_path: Path
    model: str | None = None
    paper_text: str = field(init=False)
    review_text: str = field(init=False)

    def __post_init__(self) -> None:
        self.paper_text = extract_file(self.paper_path).full_markdown
        self.review_text = self.review_path.read_text(encoding="utf-8")

    def system_prompt(self) -> str:
        return CHAT_SYSTEM

    def initial_user_message(self) -> str:
        return chat_user_initial(self.paper_text, self.review_text)
