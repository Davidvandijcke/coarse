"""Tests for coding_agent.py — OpenHands SDK wrapper.

Mirrors the HSF test pattern: mocks the openhands SDK modules since they may
not be installed. The agent writes structured output to _review_output.json;
tests mock the Conversation to simulate that file being created.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.coding_agent import (
    DEFAULT_AGENT_TOOLS,
    _OUTPUT_FILENAME,
    _resolve_agent_api_key,
)
from coarse.types import DetailedComment

# A minimal Pydantic model for testing output parsing
from pydantic import BaseModel, Field


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


def _mock_openhands_modules():
    """Create mock openhands SDK modules for patching into sys.modules."""
    mock_sdk = MagicMock()
    mock_tools = MagicMock()
    mock_terminal = MagicMock()
    mock_file_editor = MagicMock()

    mock_terminal.TerminalTool.name = "TerminalTool"
    mock_file_editor.FileEditorTool.name = "FileEditorTool"

    mock_llm_instance = MagicMock()
    mock_llm_instance.metrics.accumulated_cost = 0.01
    mock_sdk.LLM.return_value = mock_llm_instance

    return {
        "openhands": MagicMock(),
        "openhands.sdk": mock_sdk,
        "openhands.tools": mock_tools,
        "openhands.tools.terminal": mock_terminal,
        "openhands.tools.file_editor": mock_file_editor,
    }


class TestRunAgentSync:
    """Test run_agent_sync with mocked OpenHands SDK."""

    def _run_with_mock(
        self, output_data=None, output_json_str=None, write_file=True, tmp_path=None
    ):
        if tmp_path is None:
            tmp_path = Path(f"/tmp/test_coarse_agent_{os.getpid()}")
        tmp_path.mkdir(parents=True, exist_ok=True)

        mock_modules = _mock_openhands_modules()

        def mock_conversation_run(self_or_none=None):
            if write_file:
                output_path = tmp_path / _OUTPUT_FILENAME
                if output_json_str is not None:
                    output_path.write_text(output_json_str)
                elif output_data is not None:
                    output_path.write_text(json.dumps(output_data))

        mock_conversation = MagicMock()
        mock_conversation.return_value.run = mock_conversation_run
        mock_modules["openhands.sdk"].Conversation = mock_conversation

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
                )
            finally:
                output_file = tmp_path / _OUTPUT_FILENAME
                if output_file.exists():
                    output_file.unlink()

    def test_valid_output(self, tmp_path):
        """Valid JSON in _review_output.json is parsed into the schema."""
        result = self._run_with_mock(output_data=_valid_output_data(), tmp_path=tmp_path)
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
            self._run_with_mock(output_json_str="not valid json {{{", tmp_path=tmp_path)

    def test_schema_mismatch_raises(self, tmp_path):
        """Valid JSON but schema-invalid data raises RuntimeError."""
        with pytest.raises(RuntimeError, match="does not match"):
            self._run_with_mock(output_data={"unexpected_field": "value"}, tmp_path=tmp_path)

    def test_import_error(self, tmp_path):
        """Graceful error when openhands-sdk is not installed."""
        blocked = {
            "openhands": None,
            "openhands.sdk": None,
            "openhands.tools": None,
            "openhands.tools.terminal": None,
            "openhands.tools.file_editor": None,
        }
        with (
            patch.dict(sys.modules, blocked),
            patch.dict(os.environ, {"LLM_API_KEY": "test-key"}, clear=False),
        ):
            import importlib

            import coarse.coding_agent as mod

            importlib.reload(mod)
            with pytest.raises(RuntimeError, match="openhands-sdk is required"):
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

        result = self._run_with_mock(output_data=_valid_output_data(), tmp_path=tmp_path)
        assert isinstance(result, _TestOutput)
        assert result.comments[0].title == "Test issue"

    def test_timeout_triggers_error(self, tmp_path):
        """Timeout raises asyncio.TimeoutError when agent takes too long."""
        import asyncio
        import time

        mock_modules = _mock_openhands_modules()

        def slow_run():
            time.sleep(100)

        mock_conversation = MagicMock()
        mock_conversation.return_value.run = slow_run
        mock_modules["openhands.sdk"].Conversation = mock_conversation

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


class TestDefaultAgentTools:
    """Tests for the DEFAULT_AGENT_TOOLS constant."""

    def test_expected_tools(self):
        expected = ["Read", "Bash", "Glob", "Grep"]
        assert DEFAULT_AGENT_TOOLS == expected

    def test_output_filename(self):
        assert _OUTPUT_FILENAME == "_review_output.json"
