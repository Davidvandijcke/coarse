"""Abstract base classes for review agents."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Type

from pydantic import BaseModel

from coarse.config import CoarseConfig
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


class CodingReviewAgent(ABC):
    """Base class for coding agents that use OpenAI Agents SDK for deep analysis.

    Concrete subclasses implement prepare_workspace() and output_schema() to
    define the workspace layout and expected output format. The run() method
    matches the signature of the corresponding standard agent for drop-in swap.
    """

    def __init__(self, config: CoarseConfig, fallback_client: LLMClient | None = None) -> None:
        self.config = config
        self.fallback_client = fallback_client

    @abstractmethod
    def prepare_workspace(self, workspace: Path, **kwargs) -> str:
        """Write context files to workspace. Return the task prompt."""

    @abstractmethod
    def output_schema(self) -> Type[BaseModel]:
        """Return the Pydantic model class for the agent's structured output."""
