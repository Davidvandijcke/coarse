"""Tests for agents/base.py — ReviewAgent ABC."""
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient


class _DummyModel(BaseModel):
    value: str


def _make_client() -> LLMClient:
    return MagicMock(spec=LLMClient)


def test_review_agent_is_abstract():
    """Instantiating ReviewAgent directly must raise TypeError."""
    with pytest.raises(TypeError):
        ReviewAgent(_make_client())  # type: ignore[abstract]


def test_concrete_subclass_requires_run():
    """A subclass without run() must also raise TypeError on instantiation."""

    class _NoRun(ReviewAgent):
        pass

    with pytest.raises(TypeError):
        _NoRun(_make_client())  # type: ignore[abstract]


def test_concrete_subclass_run_called():
    """A complete concrete subclass can be instantiated and run() returns the expected value."""

    class _ConcreteAgent(ReviewAgent):
        def run(self, **kwargs) -> BaseModel:
            return _DummyModel(value="ok")

    agent = _ConcreteAgent(_make_client())
    result = agent.run()
    assert isinstance(result, _DummyModel)
    assert result.value == "ok"


def test_client_stored_on_instance():
    """The LLMClient passed to __init__ is accessible as self.client."""

    class _ConcreteAgent(ReviewAgent):
        def run(self, **kwargs) -> BaseModel:
            return _DummyModel(value="x")

    client = _make_client()
    agent = _ConcreteAgent(client)
    assert agent.client is client
