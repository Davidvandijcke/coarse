"""Tests for coding_agent.py — OpenAI Agents SDK wrapper.

Tests the agent wrapper and workspace tools. Mocks the agents SDK since it
may not be installed. The agent writes structured output to _review_output.json;
tests mock Runner.run() to simulate that file being created.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from coarse.coding_agent import (
    _OUTPUT_FILENAME,
    _make_workspace_tools,
    _resolve_agent_api_key,
    _ws_list_files,
    _ws_read_file,
    _ws_run_command,
    _ws_write_file,
)
from coarse.types import DetailedComment


class _TestOutput(BaseModel):
    comments: list[DetailedComment] = Field(min_length=1, max_length=5)


def _valid_output_data():
    return {
        "comments": [
            {
                "number": 1,
                "title": "Test issue",
                "quote": "Some quote from the paper.",
                "feedback": "Some feedback about the issue.",
                "severity": "major",
            }
        ]
    }


def _mock_agents_modules():
    """Create mock agents SDK modules for patching into sys.modules."""
    mock_agents = MagicMock()
    mock_litellm_ext = MagicMock()

    return {
        "agents": mock_agents,
        "agents.extensions": MagicMock(),
        "agents.extensions.models": MagicMock(),
        "agents.extensions.models.litellm_model": mock_litellm_ext,
    }


class TestRunAgentSync:
    """Test run_agent_sync with mocked OpenAI Agents SDK."""

    def _run_with_mock(
        self, output_data=None, output_json_str=None, write_file=True,
        tmp_path=None, timeout=None,
    ):
        if tmp_path is None:
            tmp_path = Path(f"/tmp/test_coarse_agent_{os.getpid()}")
        tmp_path.mkdir(parents=True, exist_ok=True)

        mock_modules = _mock_agents_modules()

        # Mock Runner.run to write _review_output.json then return
        async def mock_runner_run(*args, **kwargs):
            if write_file:
                output_path = tmp_path / _OUTPUT_FILENAME
                if output_json_str is not None:
                    output_path.write_text(output_json_str)
                elif output_data is not None:
                    output_path.write_text(json.dumps(output_data))
            return MagicMock(final_output=None)

        mock_modules["agents"].Runner.run = mock_runner_run

        with (
            patch.dict(sys.modules, mock_modules),
            patch.dict(os.environ, {"LLM_API_KEY": "test-key"}, clear=False),
        ):
            import importlib

            import coarse.coding_agent as mod

            importlib.reload(mod)

            try:
                return mod.run_agent_sync(
                    task_prompt="test",
                    system_prompt="test",
                    output_schema=_TestOutput,
                    working_directory=str(tmp_path),
                    timeout=timeout,
                )
            finally:
                output_file = tmp_path / _OUTPUT_FILENAME
                if output_file.exists():
                    output_file.unlink()

    def test_valid_output(self, tmp_path):
        """Valid JSON in _review_output.json is parsed into the schema."""
        result = self._run_with_mock(
            output_data=_valid_output_data(), tmp_path=tmp_path,
        )
        assert isinstance(result, _TestOutput)
        assert len(result.comments) == 1
        assert result.comments[0].title == "Test issue"

    def test_missing_output_file_raises(self, tmp_path):
        """Missing _review_output.json raises RuntimeError."""
        with pytest.raises(RuntimeError, match="did not produce"):
            self._run_with_mock(write_file=False, tmp_path=tmp_path)

    def test_invalid_json_raises(self, tmp_path):
        """Invalid JSON in the output file raises RuntimeError."""
        with pytest.raises(RuntimeError, match="invalid JSON"):
            self._run_with_mock(
                output_json_str="not valid json {{{", tmp_path=tmp_path,
            )

    def test_schema_mismatch_raises(self, tmp_path):
        """Valid JSON but schema-invalid data raises RuntimeError."""
        with pytest.raises(RuntimeError, match="does not match"):
            self._run_with_mock(
                output_data={"unexpected_field": "value"}, tmp_path=tmp_path,
            )

    def test_import_error(self, tmp_path):
        """Graceful error when openai-agents is not installed."""
        blocked = {
            "agents": None,
            "agents.extensions": None,
            "agents.extensions.models": None,
            "agents.extensions.models.litellm_model": None,
        }
        with (
            patch.dict(sys.modules, blocked),
            patch.dict(os.environ, {"LLM_API_KEY": "test-key"}, clear=False),
        ):
            import importlib

            import coarse.coding_agent as mod

            importlib.reload(mod)
            with pytest.raises(RuntimeError, match="openai-agents"):
                mod.run_agent_sync(
                    task_prompt="test",
                    system_prompt="test",
                    output_schema=_TestOutput,
                    working_directory=str(tmp_path),
                )

    def test_stale_output_cleaned(self, tmp_path):
        """Stale _review_output.json from a previous run is cleaned before new run."""
        stale = tmp_path / _OUTPUT_FILENAME
        stale.write_text(json.dumps({"stale": True}))

        result = self._run_with_mock(
            output_data=_valid_output_data(), tmp_path=tmp_path,
        )
        assert isinstance(result, _TestOutput)
        assert result.comments[0].title == "Test issue"

    def test_timeout_triggers_error(self, tmp_path):
        """Timeout raises asyncio.TimeoutError when agent takes too long."""
        mock_modules = _mock_agents_modules()

        async def slow_runner_run(*args, **kwargs):
            await asyncio.sleep(10)
            return MagicMock(final_output=None)

        mock_modules["agents"].Runner.run = slow_runner_run

        with (
            patch.dict(sys.modules, mock_modules),
            patch.dict(os.environ, {"LLM_API_KEY": "test-key"}, clear=False),
        ):
            import importlib

            import coarse.coding_agent as mod

            importlib.reload(mod)

            with pytest.raises(asyncio.TimeoutError):
                mod.run_agent_sync(
                    task_prompt="test",
                    system_prompt="test",
                    output_schema=_TestOutput,
                    working_directory=str(tmp_path),
                    timeout=0.01,
                )


class TestResolveAgentApiKey:
    """Tests for _resolve_agent_api_key()."""

    def test_generic_key(self):
        """LLM_API_KEY takes priority."""
        with patch.dict(os.environ, {"LLM_API_KEY": "generic"}, clear=False):
            assert _resolve_agent_api_key("anthropic/claude-haiku") == "generic"

    def test_openrouter_key_fallback(self):
        """OPENROUTER_API_KEY used for non-standard providers via resolve_api_key."""
        env = {"OPENROUTER_API_KEY": "or-key"}
        with patch.dict(os.environ, env, clear=True):
            assert _resolve_agent_api_key("moonshotai/kimi-k2.5") == "or-key"

    def test_no_key_raises(self):
        """RuntimeError when no API key is set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="No API key found"):
                _resolve_agent_api_key("any/model")


class TestWorkspaceTools:
    """Tests for workspace tool functions."""

    def test_read_file(self, tmp_path):
        """read_file reads files from workspace."""
        (tmp_path / "test.txt").write_text("hello world")
        result = _ws_read_file(tmp_path.resolve(), "test.txt")
        assert result == "hello world"

    def test_read_file_path_traversal(self, tmp_path):
        """read_file rejects path traversal."""
        result = _ws_read_file(tmp_path.resolve(), "../../etc/passwd")
        assert "path traversal" in result.lower() or "not found" in result.lower()

    def test_read_file_not_found(self, tmp_path):
        """read_file returns error for missing files."""
        result = _ws_read_file(tmp_path.resolve(), "nonexistent.txt")
        assert "not found" in result.lower()

    def test_run_command(self, tmp_path):
        """run_command executes commands in workspace."""
        (tmp_path / "test.txt").write_text("hello world")
        result = _ws_run_command(tmp_path.resolve(), "cat test.txt")
        assert "hello world" in result

    def test_list_files(self, tmp_path):
        """list_files lists workspace contents."""
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        result = _ws_list_files(tmp_path.resolve())
        assert "a.txt" in result
        assert "b.txt" in result

    def test_write_file(self, tmp_path):
        """write_file writes content to workspace."""
        result = _ws_write_file(tmp_path.resolve(), "out.json", '{"ok": true}')
        assert "OK" in result
        assert (tmp_path / "out.json").read_text() == '{"ok": true}'

    def test_write_file_path_traversal(self, tmp_path):
        """write_file rejects path traversal."""
        result = _ws_write_file(tmp_path.resolve(), "../../etc/evil", "bad")
        assert "path traversal" in result.lower()

    def test_output_filename(self):
        assert _OUTPUT_FILENAME == "_review_output.json"


class TestMakeWorkspaceTools:
    """Tests for _make_workspace_tools with comment_collector."""

    def test_without_collector_has_four_tools(self, tmp_path):
        """Without comment_collector, returns 4 tools (no add_comment)."""
        mock_agents = MagicMock()
        mock_agents.function_tool = lambda f: f  # passthrough decorator
        with patch.dict(sys.modules, {"agents": mock_agents}):
            import importlib
            import coarse.coding_agent as mod
            importlib.reload(mod)
            tools = mod._make_workspace_tools(tmp_path)
        assert len(tools) == 4

    def test_with_collector_has_five_tools(self, tmp_path):
        """With comment_collector, returns 5 tools (includes add_comment)."""
        mock_agents = MagicMock()
        mock_agents.function_tool = lambda f: f
        with patch.dict(sys.modules, {"agents": mock_agents}):
            import importlib
            import coarse.coding_agent as mod
            importlib.reload(mod)
            collector: list[dict] = []
            tools = mod._make_workspace_tools(tmp_path, comment_collector=collector)
        assert len(tools) == 5

    def test_add_comment_tool_appends_to_collector(self, tmp_path):
        """add_comment tool should append structured dicts to the collector."""
        mock_agents = MagicMock()
        mock_agents.function_tool = lambda f: f
        with patch.dict(sys.modules, {"agents": mock_agents}):
            import importlib
            import coarse.coding_agent as mod
            importlib.reload(mod)
            collector: list[dict] = []
            tools = mod._make_workspace_tools(tmp_path, comment_collector=collector)
            add_comment = tools[-1]  # last tool is add_comment
            result = add_comment(
                number=1, title="Test", quote="Some quote",
                feedback="Some feedback", severity="major",
            )
            assert len(collector) == 1
            assert collector[0]["title"] == "Test"
            assert collector[0]["quote"] == "Some quote"
            assert "OK" in result
