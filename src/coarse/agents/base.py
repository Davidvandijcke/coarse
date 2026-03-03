"""Abstract base class for all review agents."""
from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from coarse.llm import LLMClient


class ReviewAgent(ABC):
    """Base class for review agents. Each agent holds a shared LLMClient and
    implements run() to return a Pydantic model specific to that agent."""

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    @abstractmethod
    def run(self, **kwargs) -> BaseModel: ...
