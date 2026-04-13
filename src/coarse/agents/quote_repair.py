"""Quote-repair agent for batched salvage of near-miss dropped comments."""

from __future__ import annotations

from pydantic import BaseModel, Field

from coarse.agents.base import ReviewAgent
from coarse.llm import LLMClient
from coarse.prompts import QUOTE_REPAIR_SYSTEM, quote_repair_user

_TEMPERATURE = 0.0


class _QuoteRepairItem(BaseModel):
    """Single repaired-quote result."""

    number: int = Field(description="Original comment number")
    quote: str = Field(default="", description="Replacement verbatim quote or empty string")


class _QuoteRepairBatch(BaseModel):
    """Structured response envelope for batched quote repair."""

    repairs: list[_QuoteRepairItem]


class QuoteRepairAgent(ReviewAgent):
    """Batch-repair dropped quotes using bounded candidate passages."""

    def __init__(self, client: LLMClient) -> None:
        super().__init__(client)

    def run(self, items: list[dict[str, object]]) -> dict[int, str]:  # type: ignore[override]
        if not items:
            return {}
        messages = self._build_messages(QUOTE_REPAIR_SYSTEM, quote_repair_user(items))
        result = self.client.complete(
            messages,
            _QuoteRepairBatch,
            max_tokens=8192,
            temperature=_TEMPERATURE,
        )
        return {item.number: item.quote for item in result.repairs}
