"""OpenAI Agents SDK wrapper for autonomous coding agents.

Provides run_agent() which invokes an agent with workspace tools and returns
structured Pydantic output. The primary output mechanism is tool-based: agents
call add_comment() for each issue found. File-based output (_review_output.json)
is supported as a fallback.

Used by CodingSectionAgent and CodingCritiqueAgent for deep paper analysis.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Type, Union

from pydantic import BaseModel, ValidationError

from coarse.config import CoarseConfig, resolve_api_key
from coarse.llm import _normalize_model
from coarse.models import AGENT_MODEL

logger = logging.getLogger(__name__)

# Filename the agent writes structured output to
_OUTPUT_FILENAME = "_review_output.json"


def _resolve_agent_api_key(
    model: Optional[str] = None, config: Optional[CoarseConfig] = None,
) -> str:
    """Resolve API key for the agent model.

    Checks LLM_API_KEY (generic), then delegates to coarse's resolve_api_key().

    Raises:
        RuntimeError: If no API key is found.
    """
    generic = os.getenv("LLM_API_KEY")
    if generic:
        return generic

    resolved = resolve_api_key(model or AGENT_MODEL, config)
    if resolved:
        return resolved

    raise RuntimeError(
        "No API key found for coding agent. Set one of: "
        "LLM_API_KEY, OPENROUTER_API_KEY, or the provider-specific key."
    )


def _resolve_in_workspace(workspace: Path, relative: str) -> Path:
    """Resolve *relative* inside *workspace*, rejecting path traversal."""
    resolved = (workspace / relative).resolve()
    ws_resolved = workspace.resolve()
    if not resolved.is_relative_to(ws_resolved):
        raise ValueError("path traversal not allowed")
    return resolved


def _ws_read_file(workspace: Path, path: str) -> str:
    """Read a file from the workspace directory."""
    try:
        resolved = _resolve_in_workspace(workspace, path)
    except ValueError as e:
        return f"Error: {e}"
    if not resolved.exists():
        return f"Error: file not found: {path}"
    try:
        return resolved.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"


def _ws_run_command(workspace: Path, command: str) -> str:
    """Run a shell command in the workspace directory."""
    try:
        result = subprocess.run(
            command, shell=True, cwd=str(workspace),
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        if len(output) > 10000:
            output = output[:10000] + "\n... (truncated)"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: command timed out (30s limit)"
    except Exception as e:
        return f"Error running command: {e}"


def _ws_list_files(workspace: Path, directory: str = ".") -> str:
    """List files in a workspace directory."""
    try:
        target = _resolve_in_workspace(workspace, directory)
    except ValueError as e:
        return f"Error: {e}"
    if not target.exists():
        return f"Error: directory not found: {directory}"
    entries = sorted(target.iterdir())
    return "\n".join(
        f"{'[dir] ' if e.is_dir() else ''}{e.name}" for e in entries
    )


def _ws_write_file(workspace: Path, path: str, content: str) -> str:
    """Write content to a file in the workspace directory."""
    try:
        resolved = _resolve_in_workspace(workspace, path)
    except ValueError as e:
        return f"Error: {e}"
    try:
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"OK: wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def _make_workspace_tools(
    workspace: Path,
    comment_collector: list[dict] | None = None,
) -> list:
    """Create workspace-scoped tools for the agent.

    Wraps workspace helper functions with @function_tool for the SDK.

    Args:
        workspace: Working directory for the agent.
        comment_collector: If provided, an add_comment tool is created that
            appends structured comments to this list. The SDK serializes
            tool call arguments automatically, so the agent never has to
            write raw JSON containing LaTeX backslashes.
    """
    from agents import function_tool

    workspace_resolved = workspace.resolve()

    @function_tool
    def read_file(path: str) -> str:
        """Read a file from the workspace directory."""
        return _ws_read_file(workspace_resolved, path)

    @function_tool
    def run_command(command: str) -> str:
        """Run a shell command in the workspace directory. Use for grep, python, etc."""
        return _ws_run_command(workspace_resolved, command)

    @function_tool
    def list_files(directory: str = ".") -> str:
        """List files in a workspace directory."""
        return _ws_list_files(workspace_resolved, directory)

    @function_tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file in the workspace directory."""
        return _ws_write_file(workspace_resolved, path, content)

    tools = [read_file, run_command, list_files, write_file]

    if comment_collector is not None:
        @function_tool
        def add_comment(
            number: int,
            title: str,
            quote: str,
            feedback: str,
            severity: str = "major",
        ) -> str:
            """Add a review comment. Call once per issue found."""
            comment_collector.append({
                "number": number,
                "title": title,
                "quote": quote,
                "feedback": feedback,
                "severity": severity,
            })
            return f"OK: comment #{number} '{title}' recorded ({len(comment_collector)} total)"

        tools.append(add_comment)

    return tools


async def run_agent(
    task_prompt: str,
    system_prompt: str,
    output_schema: Type[BaseModel],
    working_directory: Union[str, Path],
    max_turns: int = 15,
    model: Optional[str] = None,
    max_budget_usd: Optional[float] = None,
    timeout: Optional[float] = None,
    config: Optional[CoarseConfig] = None,
) -> BaseModel:
    """Run an autonomous agent via OpenAI Agents SDK and return structured output.

    The agent uses workspace tools (read_file, run_command, list_files) to
    analyze paper content, then writes structured JSON to _review_output.json.
    We parse and validate the file against output_schema.

    Uses file-based output instead of the SDK's output_type for compatibility
    with models that don't support tool-calling-based structured output
    (e.g. Qwen, DeepSeek via OpenRouter).

    Args:
        task_prompt: The task for the agent to complete.
        system_prompt: System prompt for the agent.
        output_schema: Pydantic model class for structured output.
        working_directory: Working directory for the agent.
        max_turns: Maximum conversation turns.
        model: Model ID in provider/model format.
        max_budget_usd: Maximum cost in USD (advisory, logged only).
        timeout: Timeout in seconds. None = no timeout.
        config: CoarseConfig for API key resolution.

    Returns:
        Parsed Pydantic model instance.

    Raises:
        RuntimeError: If the agent fails or SDK is not installed.
    """
    try:
        from agents import Agent, Runner, tracing
        from agents.extensions.models.litellm_model import LitellmModel
    except ImportError as e:
        raise RuntimeError(
            "openai-agents[litellm] is required for coding agents. "
            "Install with: pip install coarse[agentic]"
        ) from e

    # Disable SDK tracing — it has a recursion bug on large payloads
    tracing.set_tracing_disabled(True)

    resolved_model = _normalize_model(model or AGENT_MODEL)
    api_key = _resolve_agent_api_key(model or AGENT_MODEL, config)

    litellm_model = LitellmModel(model=resolved_model, api_key=api_key)

    working_dir = Path(working_directory).resolve()
    working_dir.mkdir(parents=True, exist_ok=True)

    # Clean up stale output from a previous run
    output_path = working_dir / _OUTPUT_FILENAME
    if output_path.exists():
        output_path.unlink()

    # Tool-based output: agent calls add_comment() instead of writing JSON
    collected_comments: list[dict] = []
    tools = _make_workspace_tools(working_dir, comment_collector=collected_comments)

    # Inject structured output instructions into system prompt
    schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        f"OUTPUT: Call `add_comment(number, title, quote, feedback, severity)` "
        f"for each issue you find. The SDK handles JSON serialization — "
        f"just pass arguments directly. Do NOT manually write JSON files.\n\n"
        f"As a fallback, you may also write valid JSON to "
        f"`{_OUTPUT_FILENAME}` using write_file.\n\n"
        f"Output schema:\n```json\n{schema_json}\n```"
    )

    agent = Agent(
        name="paper-reviewer",
        instructions=full_system,
        model=litellm_model,
        tools=tools,
    )

    if max_budget_usd:
        logger.info("Agent budget cap: $%.2f (advisory)", max_budget_usd)

    if timeout is not None:
        await asyncio.wait_for(
            Runner.run(agent, task_prompt, max_turns=max_turns),
            timeout=timeout,
        )
    else:
        await Runner.run(agent, task_prompt, max_turns=max_turns)

    # Resolve output: (1) tool-collected comments, (2) file fallback
    if collected_comments:
        logger.info(
            "Agent produced %d comments via add_comment tool", len(collected_comments)
        )
        data = {"comments": collected_comments}
        try:
            return output_schema.model_validate(data)
        except ValidationError as e:
            logger.warning("Tool-collected comments failed validation: %s", e)
            # Fall through to file-based output

    # File-based fallback
    if not output_path.exists():
        raise RuntimeError(
            f"Agent did not produce output (no add_comment calls and no {_OUTPUT_FILENAME}). "
            "The agent may have failed or not followed output instructions."
        )

    try:
        raw = output_path.read_text().strip()
        # Strip markdown fences if the agent wrapped JSON in ```json ... ```
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [ln for ln in lines if not ln.strip().startswith("```")]
            raw = "\n".join(lines)
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try fixing common LLM JSON errors (unescaped backslashes, etc.)
        import re
        try:
            fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', raw)
            data = json.loads(fixed)
            logger.info("Fixed invalid JSON escapes in agent output")
        except json.JSONDecodeError as e2:
            raise RuntimeError(
                f"Agent wrote invalid JSON to {_OUTPUT_FILENAME}: {e2}"
            ) from e2

    try:
        return output_schema.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(
            f"Agent output does not match {output_schema.__name__} schema: {e}"
        ) from e


def run_agent_sync(
    task_prompt: str,
    system_prompt: str,
    output_schema: Type[BaseModel],
    working_directory: Union[str, Path],
    max_turns: int = 15,
    model: Optional[str] = None,
    max_budget_usd: Optional[float] = None,
    timeout: Optional[float] = None,
    config: Optional[CoarseConfig] = None,
) -> BaseModel:
    """Synchronous wrapper around run_agent()."""
    try:
        asyncio.get_running_loop()
        raise RuntimeError(
            "run_agent_sync() cannot be called from an async context. "
            "Use await run_agent() instead."
        )
    except RuntimeError as e:
        if "no current event loop" not in str(e) and "no running event loop" not in str(e):
            raise
    return asyncio.run(
        run_agent(
            task_prompt=task_prompt,
            system_prompt=system_prompt,
            output_schema=output_schema,
            working_directory=working_directory,
            max_turns=max_turns,
            model=model,
            max_budget_usd=max_budget_usd,
            timeout=timeout,
            config=config,
        )
    )
