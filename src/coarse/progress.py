"""Pipeline progress event types."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

PipelineProgressEvent = Literal["started", "updated", "completed"]


@dataclass(frozen=True, slots=True)
class PipelineProgress:
    """A single pipeline progress update emitted during review execution."""

    event: PipelineProgressEvent
    stage_key: str
    stage_label: str
    completed_stages: int
    total_stages: int
    actual_cost_usd: float


PipelineProgressCallback = Callable[[PipelineProgress], None]
