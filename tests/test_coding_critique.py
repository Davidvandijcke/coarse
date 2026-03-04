"""Tests for agents/coding_critique.py — CodingCritiqueAgent.

Mocks run_agent_sync to test workspace preparation and output parsing.
Tests fallback to standard CritiqueAgent on failure.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.agents.coding_critique import CodingCritiqueAgent
from coarse.agents.critique import _RevisedComments
from coarse.config import CoarseConfig
from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    SectionInfo,
    SectionType,
)


def _make_config() -> CoarseConfig:
    return CoarseConfig(
        default_model="openai/gpt-4o-mini",
        use_coding_agents=True,
    )


def _make_overview() -> OverviewFeedback:
    return OverviewFeedback(
        summary="A paper about methods.",
        issues=[OverviewIssue(title="Issue 1", body="Description of issue.")],
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote="Some quoted text from the paper.",
        feedback="Feedback about the issue.",
        severity="major",
    )


def _make_section(number: int = 1) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=f"Section {number}",
        text="Section content here.",
        section_type=SectionType.INTRODUCTION,
    )


def _valid_critique_output() -> _RevisedComments:
    return _RevisedComments(comments=[_make_comment()])


class TestPrepareWorkspace:
    """Test that prepare_workspace writes correct files."""

    def test_writes_paper_md(self, tmp_path):
        agent = CodingCritiqueAgent(_make_config())
        agent.prepare_workspace(
            tmp_path,
            paper_markdown="Full paper text.",
            overview=_make_overview(),
            comments=[_make_comment()],
        )
        assert (tmp_path / "paper.md").exists()
        assert (tmp_path / "paper.md").read_text() == "Full paper text."

    def test_writes_overview_json(self, tmp_path):
        agent = CodingCritiqueAgent(_make_config())
        overview = _make_overview()
        agent.prepare_workspace(
            tmp_path,
            paper_markdown="paper",
            overview=overview,
            comments=[_make_comment()],
        )
        data = json.loads((tmp_path / "overview.json").read_text())
        assert data["issues"][0]["title"] == "Issue 1"

    def test_writes_comments_json(self, tmp_path):
        agent = CodingCritiqueAgent(_make_config())
        comments = [_make_comment(1), _make_comment(2)]
        agent.prepare_workspace(
            tmp_path,
            paper_markdown="paper",
            overview=_make_overview(),
            comments=comments,
        )
        data = json.loads((tmp_path / "comments.json").read_text())
        assert len(data) == 2
        assert data[0]["number"] == 1
        assert data[1]["number"] == 2

    def test_writes_sections_dir(self, tmp_path):
        agent = CodingCritiqueAgent(_make_config())
        sections = [_make_section(1), _make_section(2)]
        agent.prepare_workspace(
            tmp_path,
            paper_markdown="paper",
            overview=_make_overview(),
            comments=[_make_comment()],
            all_sections=sections,
        )
        sections_dir = tmp_path / "sections"
        assert sections_dir.exists()
        assert len(list(sections_dir.iterdir())) == 2

    def test_writes_example_output(self, tmp_path):
        agent = CodingCritiqueAgent(_make_config())
        agent.prepare_workspace(
            tmp_path,
            paper_markdown="paper",
            overview=_make_overview(),
            comments=[_make_comment()],
        )
        example = json.loads((tmp_path / "example_output.json").read_text())
        assert "comments" in example
        assert len(example["comments"]) == 1

    def test_returns_task_prompt(self, tmp_path):
        agent = CodingCritiqueAgent(_make_config())
        prompt = agent.prepare_workspace(
            tmp_path,
            paper_markdown="paper",
            overview=_make_overview(),
            comments=[_make_comment(1), _make_comment(2)],
        )
        assert "quality evaluation" in prompt.lower()
        assert "_review_output.json" in prompt


class TestCodingCritiqueRun:
    """Test run() with mocked run_agent_sync."""

    @patch("coarse.agents.coding_critique.run_agent_sync")
    def test_successful_run(self, mock_run):
        """Successful coding agent returns revised comments."""
        mock_run.return_value = _valid_critique_output()
        agent = CodingCritiqueAgent(_make_config())
        result = agent.run(
            _make_overview(), [_make_comment()],
            paper_markdown="Full paper",
        )
        assert len(result) == 1
        assert result[0].title == "Comment 1"
        mock_run.assert_called_once()

    @patch("coarse.agents.coding_critique.run_agent_sync")
    def test_fallback_on_failure(self, mock_run):
        """RuntimeError falls back to standard CritiqueAgent."""
        mock_run.side_effect = RuntimeError("Agent failed")
        mock_client = MagicMock()
        mock_client.complete.return_value = _valid_critique_output()

        agent = CodingCritiqueAgent(_make_config(), fallback_client=mock_client)
        result = agent.run(
            _make_overview(), [_make_comment()],
            paper_markdown="Full paper",
        )
        mock_client.complete.assert_called_once()

    @patch("coarse.agents.coding_critique.run_agent_sync")
    def test_no_fallback_client_reraises(self, mock_run):
        """Without fallback_client, RuntimeError propagates."""
        mock_run.side_effect = RuntimeError("Agent failed")
        agent = CodingCritiqueAgent(_make_config(), fallback_client=None)
        with pytest.raises(RuntimeError, match="Agent failed"):
            agent.run(
                _make_overview(), [_make_comment()],
                paper_markdown="Full paper",
            )

    @patch("coarse.agents.coding_critique.run_agent_sync")
    def test_comment_target_passed_to_prompt(self, mock_run):
        """comment_target is used in the system prompt."""
        mock_run.return_value = _valid_critique_output()
        agent = CodingCritiqueAgent(_make_config())
        agent.run(
            _make_overview(), [_make_comment()],
            comment_target=15,
            paper_markdown="Full paper",
        )
        # Verify system_prompt was passed through
        call_kwargs = mock_run.call_args.kwargs
        assert "15" in call_kwargs["system_prompt"]
