"""Tests for multi-judge overview panel."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from coarse.agents.overview import OverviewAgent, synthesize_overviews
from coarse.llm import LLMClient
from coarse.prompts import OVERVIEW_PERSONAS, OVERVIEW_SYNTHESIS_SYSTEM
from coarse.types import (
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    SectionInfo,
    SectionType,
)


def _make_overview(n_issues: int = 4) -> OverviewFeedback:
    return OverviewFeedback(
        issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}") for i in range(1, n_issues + 1)]
    )


def _make_structure() -> PaperStructure:
    return PaperStructure(
        title="Test",
        domain="test",
        taxonomy="test",
        abstract="Abstract",
        sections=[
            SectionInfo(
                number=1, title="Intro", text="x" * 600,
                section_type=SectionType.INTRODUCTION,
            ),
        ],
    )


def test_three_personas_defined():
    """OVERVIEW_PERSONAS has exactly 3 entries."""
    assert len(OVERVIEW_PERSONAS) == 3


def test_run_panel_calls_three_judges():
    """run_panel makes 3 parallel calls with different personas."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.supports_prompt_caching = False
    agent = OverviewAgent(mock_client)

    overview = _make_overview()
    synthesized = _make_overview(5)

    # Mock run to return overview, and synthesize_overviews
    with patch.object(agent, "run", return_value=overview) as mock_run:
        with patch("coarse.agents.overview.synthesize_overviews", return_value=synthesized):
            agent.run_panel(_make_structure())

    assert mock_run.call_count == 3
    # Each call should have a different persona
    personas_used = [call.kwargs.get("persona") or call.args[2] for call in mock_run.call_args_list]
    assert len(set(personas_used)) == 3


def test_run_panel_single_judge_fallback():
    """If only 1 judge succeeds, return its result directly."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.supports_prompt_caching = False
    agent = OverviewAgent(mock_client)

    overview = _make_overview()
    call_count = 0

    def run_with_failures(structure, calibration=None, persona=None, literature_context=""):
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            raise RuntimeError("Judge failed")
        return overview

    with patch.object(agent, "run", side_effect=run_with_failures):
        result = agent.run_panel(_make_structure())

    assert result == overview


def test_run_panel_all_fail_raises():
    """If all judges fail, RuntimeError is raised."""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.supports_prompt_caching = False
    agent = OverviewAgent(mock_client)

    with patch.object(agent, "run", side_effect=RuntimeError("fail")):
        with pytest.raises(RuntimeError, match="All overview judges failed"):
            agent.run_panel(_make_structure())


def test_synthesize_overviews_calls_llm():
    """synthesize_overviews makes a single LLM call with synthesis prompt."""
    mock_client = MagicMock()
    synthesized = _make_overview(5)
    mock_client.complete.return_value = synthesized

    overviews = [_make_overview(4), _make_overview(4), _make_overview(4)]
    result = synthesize_overviews(overviews, mock_client)

    mock_client.complete.assert_called_once()
    call_args = mock_client.complete.call_args
    messages = call_args[0][0]
    assert messages[0]["content"] == OVERVIEW_SYNTHESIS_SYSTEM
    assert result == synthesized
