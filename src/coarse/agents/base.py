"""Abstract base classes for review agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from coarse.llm import LLMClient

if TYPE_CHECKING:
    from coarse.types import SectionInfo


def section_filename(s: SectionInfo) -> str:
    """Generate a safe filename from a section number and title."""
    slug = s.title.lower().replace(" ", "_")[:40]
    prefix = f"{s.number:02}" if isinstance(s.number, int) else str(s.number)
    return f"{prefix}_{slug}.md"


class ReviewAgent(ABC):
    """Base class for review agents. Each agent holds a shared LLMClient and
    implements run() to return a Pydantic model specific to that agent."""

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    @abstractmethod
    def run(self, **kwargs) -> BaseModel: ...

    def _build_messages(
        self, system: str, user: str,
    ) -> list[dict]:
        """Build messages list, adding cache_control on system prompt for Anthropic."""
        if self.client.supports_prompt_caching:
            return [
                {"role": "system", "content": [
                    {"type": "text", "text": system,
                     "cache_control": {"type": "ephemeral"}},
                ]},
                {"role": "user", "content": user},
            ]
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
