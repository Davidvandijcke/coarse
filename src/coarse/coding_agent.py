"""OpenHands SDK wrapper for autonomous coding agents.

Adapted from HSF's onboard/coding_agent.py. Provides run_agent() which invokes
an OpenHands agent with tools and returns structured Pydantic output.

Used by CodingSectionAgent and CodingCritiqueAgent for deep paper analysis.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import List, Optional, Type, Union

from pydantic import BaseModel, ValidationError

from coarse.config import CoarseConfig, resolve_api_key
from coarse.models import AGENT_MODEL

logger = logging.getLogger(__name__)

DEFAULT_AGENT_TOOLS = ["Read", "Bash", "Glob", "Grep"]

# Filename the agent writes structured output to
_OUTPUT_FILENAME = "_review_output.json"


def _resolve_agent_api_key(model: Optional[str] = None, config: Optional[CoarseConfig] = None) -> str:
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


async def run_agent(
    task_prompt: str,
    system_prompt: str,
    output_schema: Type[BaseModel],
    working_directory: Union[str, Path],
    allowed_tools: Optional[List[str]] = None,
    max_turns: int = 15,
    model: Optional[str] = None,
    max_budget_usd: Optional[float] = None,
    timeout: Optional[float] = None,
    config: Optional[CoarseConfig] = None,
) -> BaseModel:
    """Run an autonomous agent via OpenHands SDK and return structured output.

    The agent executes tools (terminal, file editor) to complete the task,
    then writes its result as JSON to _review_output.json.

    Args:
        task_prompt: The task for the agent to complete.
        system_prompt: System prompt for the agent.
        output_schema: Pydantic model class for structured output.
        working_directory: Working directory for the agent.
        allowed_tools: Tool names (currently informational).
        max_turns: Maximum conversation turns.
        model: Model ID in provider/model format.
        max_budget_usd: Maximum cost in USD (advisory).
        timeout: Timeout in seconds. None = no timeout.
        config: CoarseConfig for API key resolution.

    Returns:
        Parsed Pydantic model instance.

    Raises:
        RuntimeError: If the agent fails or produces invalid output.
    """
    try:
        from openhands.sdk import LLM, Agent, AgentContext, Conversation, Tool
        import openhands.tools  # noqa: F401 — triggers tool registration
    except ImportError as e:
        raise RuntimeError(
            "openhands-sdk and openhands-tools are required for coding agents. "
            "Install with: pip install coarse[agentic]"
        ) from e

    resolved_model = model or AGENT_MODEL
    api_key = _resolve_agent_api_key(resolved_model, config)

    llm = LLM(
        model=resolved_model,
        api_key=api_key,
        base_url=os.getenv("LLM_BASE_URL"),
    )

    tools = [
        Tool(name="terminal"),
        Tool(name="file_editor"),
    ]

    # Inject structured output instructions into system prompt
    schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
    full_system = (
        f"{system_prompt}\n\n"
        f"CRITICAL REQUIREMENT: When you complete the task, you MUST write your "
        f"final result as valid JSON to a file named `{_OUTPUT_FILENAME}` in "
        f"the working directory. The JSON must conform to this schema:\n"
        f"```json\n{schema_json}\n```\n"
        f"Do NOT skip this step. The file must exist when you are done."
    )

    context = AgentContext(system_message_suffix=full_system)
    agent = Agent(llm=llm, tools=tools, agent_context=context)

    if max_budget_usd:
        logger.info("Agent budget cap: $%.2f (advisory)", max_budget_usd)

    working_dir = Path(working_directory).resolve()
    working_dir.mkdir(parents=True, exist_ok=True)

    # Clean up stale output from a previous run
    output_path = working_dir / _OUTPUT_FILENAME
    if output_path.exists():
        output_path.unlink()

    conversation = Conversation(agent=agent, workspace=str(working_dir))
    conversation.send_message(task_prompt)

    # conversation.run() is synchronous in OpenHands SDK.
    # Use asyncio.to_thread for timeout support.
    if timeout is not None:
        await asyncio.wait_for(
            asyncio.to_thread(conversation.run), timeout=timeout
        )
    else:
        conversation.run()

    # Log cost if available
    try:
        cost = llm.metrics.accumulated_cost
        logger.info("Agent cost: $%.4f", cost)
        if max_budget_usd and cost > max_budget_usd:
            logger.warning("Agent exceeded budget: $%.4f > $%.4f", cost, max_budget_usd)
    except Exception:
        pass

    # Read structured output from file
    if not output_path.exists():
        raise RuntimeError(
            f"Agent did not produce {_OUTPUT_FILENAME}. "
            "The agent may have failed or not followed output instructions."
        )

    try:
        raw = output_path.read_text().strip()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Agent wrote invalid JSON to {_OUTPUT_FILENAME}: {e}") from e

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
    allowed_tools: Optional[List[str]] = None,
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
            allowed_tools=allowed_tools,
            max_turns=max_turns,
            model=model,
            max_budget_usd=max_budget_usd,
            timeout=timeout,
            config=config,
        )
    )
