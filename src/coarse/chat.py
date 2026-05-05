"""Chat-mode reviewer: interactive Q&A over a paper + prior review.

Stateless from the LLM's perspective on each turn — we resend the full
message history every call. The system prompt names the literature-search
sentinel; the chat loop intercepts it and calls Perplexity. See cli_chat.py
for the REPL wrapper.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from coarse.extraction import extract_file
from coarse.llm import LLMClient
from coarse.models import LITERATURE_SEARCH_MODEL
from coarse.prompts import CHAT_SYSTEM, PERPLEXITY_SYSTEM, chat_user_initial

_SEARCH_SENTINEL_RE = re.compile(r"<<SEARCH:\s*(.+?)\s*>>", re.DOTALL)
_MAX_SEARCHES_PER_TURN = 3


def _extract_search_query(reply: str) -> str | None:
    """Return the first <<SEARCH: ...>> query, or None."""
    match = _SEARCH_SENTINEL_RE.search(reply)
    return match.group(1).strip() if match else None


def run_literature_query(query: str) -> str:
    """One-shot Perplexity Sonar Pro lookup. Returns the raw markdown reply."""
    lit_client = LLMClient(model=LITERATURE_SEARCH_MODEL)
    messages = [
        {"role": "system", "content": PERPLEXITY_SYSTEM},
        {"role": "user", "content": query},
    ]
    return lit_client.complete_text(messages, max_tokens=4096, temperature=0.3, timeout=60)


@dataclass
class ChatSession:
    paper_path: Path
    review_path: Path
    model: str | None = None
    paper_text: str = field(init=False)
    review_text: str = field(init=False)
    history: list[dict] = field(init=False, default_factory=list)
    _client: LLMClient | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self.paper_text = extract_file(self.paper_path).full_markdown
        self.review_text = self.review_path.read_text(encoding="utf-8")
        self.history = [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": self.initial_user_message()},
        ]

    def system_prompt(self) -> str:
        return CHAT_SYSTEM

    def initial_user_message(self) -> str:
        return chat_user_initial(self.paper_text, self.review_text)

    def _client_or_create(self) -> LLMClient:
        if self._client is None:
            self._client = LLMClient(model=self.model)
        return self._client

    def ask(self, question: str) -> str:
        """Send a user question. Honor up to N search-sentinel hops before returning."""
        self.history.append({"role": "user", "content": question})
        client = self._client_or_create()

        for _ in range(_MAX_SEARCHES_PER_TURN + 1):  # +1 so we get one final non-search reply
            reply = client.complete_text(self.history, max_tokens=4096, temperature=0.3)
            self.history.append({"role": "assistant", "content": reply})

            query = _extract_search_query(reply)
            if query is None:
                return reply

            results = run_literature_query(query)
            self.history.append(
                {
                    "role": "user",
                    "content": (
                        f"Literature search results for `{query}`:\n\n{results}\n\n"
                        "Continue your answer using these results."
                    ),
                }
            )

        # Hit the search cap — return whatever the model said last.
        return reply
