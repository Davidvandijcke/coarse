"""The tool-calling loop one agent runs inside (#264).

An agent here is: a system prompt, a task, a bounded tool set over one
workspace, and a typed result it must deliberately submit. The loop ends when
the agent calls ``submit``, when it stops asking for tools, or when it runs out
of turns or tool budget.

Submission is itself a tool call whose parameters are the result model's JSON
schema. That keeps the structured output in the same turn as the agent's
reasoning, rather than needing a second summarizing pass that can quietly drop
the evidence an investigator gathered.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from coarse.agent.tools import ToolBox
from coarse.agent.types import AgentRunRecord
from coarse.llm import LLMClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

DEFAULT_MAX_TURNS = 24
# Tool results are fed straight back into context. A single huge result (a
# whole 14k-char appendix) is fine; an agent that reads twenty of them is not,
# so the per-result cap is generous and the tool-call budget is the real bound.
MAX_TOOL_RESULT_CHARS = 60_000


@dataclass
class AgentResult:
    """What one agent run produced."""

    record: AgentRunRecord
    result: BaseModel | None = None
    text: str = ""
    transcript: list[dict] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.transcript is None:
            self.transcript = []


def _submit_schema(model: type[BaseModel], description: str) -> dict[str, Any]:
    """Wrap a Pydantic model as a `submit` function tool."""
    schema = model.model_json_schema()
    # Providers reject $defs-only roots inconsistently; keep the schema whole
    # and let the provider resolve internal refs, which both OpenAI- and
    # Anthropic-compatible OpenRouter routes do.
    return {
        "type": "function",
        "function": {
            "name": "submit",
            "description": description,
            "parameters": schema,
        },
    }


def run_agent(
    client: LLMClient,
    *,
    role: str,
    agent_id: str,
    system: str,
    task: str,
    toolbox: ToolBox,
    submit_model: type[T],
    submit_description: str = "Submit your final result. Call this exactly once, when done.",
    max_turns: int = DEFAULT_MAX_TURNS,
    max_tokens: int = 8192,
    temperature: float = 0.2,
) -> AgentResult:
    """Run one agent to completion and return its typed result.

    Never raises on agent misbehaviour: a loop that times out, returns
    unparseable arguments, or errors at the provider yields an
    ``AgentResult`` with ``result=None`` and the reason in
    ``record.error``. The orchestrator treats that as "this agent found
    nothing", which is a valid outcome.
    """
    started = time.monotonic()
    record = AgentRunRecord(role=role, agent_id=agent_id, model=client.model)
    cost_before = client.cost_usd

    tools = toolbox.schemas() + [_submit_schema(submit_model, submit_description)]
    messages: list[dict] = [
        {"role": "system", "content": system},
        {"role": "user", "content": task},
    ]
    result: BaseModel | None = None
    last_text = ""

    for turn in range(max_turns):
        record.turns = turn + 1
        try:
            message = client.complete_with_tools(
                messages,
                tools,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as exc:  # noqa: BLE001 - recorded, not raised
            logger.warning("agent %s (%s) provider call failed: %s", agent_id, role, exc)
            record.error = f"provider call failed on turn {turn + 1}: {exc}"
            break

        messages.append(message)
        if message.get("content"):
            last_text = str(message["content"])

        calls = message.get("tool_calls") or []
        if not calls:
            # The agent stopped asking for tools without submitting. Prompt it
            # once to submit, then stop.
            if result is None and turn < max_turns - 1:
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Call `submit` now with your result. If you found nothing that "
                            "meets the bar, submit an empty result — that is a valid answer."
                        ),
                    }
                )
                continue
            break

        finished = False
        for call in calls:
            name = call["function"]["name"]
            raw_args = call["function"].get("arguments") or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}
                tool_out = (
                    "TOOL ERROR: your arguments were not valid JSON. Resend them as a "
                    "single JSON object with correctly escaped backslashes."
                )
            else:
                tool_out = ""

            if name == "submit":
                if tool_out:
                    messages.append(_tool_msg(call, tool_out))
                    continue
                try:
                    result = submit_model.model_validate(args)
                    messages.append(_tool_msg(call, "Submitted."))
                    finished = True
                except ValidationError as exc:
                    messages.append(
                        _tool_msg(
                            call,
                            "SUBMIT REJECTED — your result did not match the schema:\n"
                            f"{exc}\n\nFix it and call `submit` again.",
                        )
                    )
                continue

            record.tool_calls += 1
            if not tool_out:
                tool_out = toolbox.dispatch(name, args)
            messages.append(_tool_msg(call, tool_out[:MAX_TOOL_RESULT_CHARS]))

        if finished:
            break

    if result is None and not record.error:
        record.error = f"no result submitted within {record.turns} turns"

    record.cost_usd = client.cost_usd - cost_before
    record.duration_s = time.monotonic() - started
    return AgentResult(record=record, result=result, text=last_text, transcript=messages)


def _tool_msg(call: dict, content: str) -> dict:
    return {
        "role": "tool",
        "tool_call_id": call.get("id") or "",
        "name": call["function"]["name"],
        "content": content,
    }
