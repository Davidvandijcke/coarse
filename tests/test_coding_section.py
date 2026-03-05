"""Tests for agents/coding_section.py — CodingSectionAgent.

Mocks run_agent_sync (not the full SDK) to test workspace preparation
and output parsing. Tests fallback to standard SectionAgent on failure.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from coarse.agents.coding_section import CodingSectionAgent
from coarse.agents.section import _SectionComments
from coarse.config import CoarseConfig
from coarse.types import (
    DetailedComment,
    DomainCalibration,
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


def _make_section(
    number: int = 1,
    title: str = "Methodology",
    section_type: SectionType = SectionType.METHODOLOGY,
) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=title,
        text="We propose a novel method based on X. The key equation is y = mx + b.",
        section_type=section_type,
        claims=["Method converges in O(n) time"],
        definitions=["X := the input space"],
    )


def _make_overview() -> OverviewFeedback:
    return OverviewFeedback(
        summary="A paper about methods.",
        issues=[OverviewIssue(title="Convergence claim", body="The convergence proof has gaps.")],
    )


def _make_calibration() -> DomainCalibration:
    return DomainCalibration(
        methodology_concerns=["Identification strategy"],
        assumption_red_flags=["Linearity"],
        what_not_to_check=["Formatting"],
        evaluation_standards=["Top-5 journal"],
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title="Test issue",
        quote="We propose a novel method based on X.",
        feedback="The method lacks justification.",
        severity="major",
    )


def _valid_section_output() -> _SectionComments:
    return _SectionComments(comments=[_make_comment()])


class TestPrepareWorkspace:
    """Test that prepare_workspace writes correct files."""

    def test_writes_paper_md(self, tmp_path):
        agent = CodingSectionAgent(_make_config())
        section = _make_section()
        agent.prepare_workspace(
            tmp_path,
            section=section,
            paper_markdown="Full paper text here.",
            all_sections=[section],
            paper_title="Test Paper",
        )
        assert (tmp_path / "paper.md").exists()
        assert (tmp_path / "paper.md").read_text() == "Full paper text here."

    def test_writes_section_md_with_metadata(self, tmp_path):
        agent = CodingSectionAgent(_make_config())
        section = _make_section()
        agent.prepare_workspace(
            tmp_path,
            section=section,
            paper_markdown="paper",
            all_sections=[section],
            paper_title="Test Paper",
        )
        content = (tmp_path / "section.md").read_text()
        assert "Section 1: Methodology" in content
        assert "Type: methodology" in content
        assert "Claims:" in content
        assert "Definitions:" in content
        assert section.text in content

    def test_writes_other_sections(self, tmp_path):
        agent = CodingSectionAgent(_make_config())
        section = _make_section(1, "Methodology")
        other = _make_section(2, "Results", SectionType.RESULTS)
        agent.prepare_workspace(
            tmp_path,
            section=section,
            paper_markdown="paper",
            all_sections=[section, other],
            paper_title="Test Paper",
        )
        other_dir = tmp_path / "other_sections"
        assert other_dir.exists()
        files = list(other_dir.iterdir())
        assert len(files) == 1
        assert "results" in files[0].name.lower()

    def test_writes_context_json(self, tmp_path):
        agent = CodingSectionAgent(_make_config())
        section = _make_section()
        overview = _make_overview()
        calibration = _make_calibration()
        agent.prepare_workspace(
            tmp_path,
            section=section,
            paper_markdown="paper",
            all_sections=[section],
            paper_title="Test Paper",
            overview=overview,
            calibration=calibration,
            literature_context="Some lit context",
        )
        ctx = json.loads((tmp_path / "context.json").read_text())
        assert ctx["paper_title"] == "Test Paper"
        assert len(ctx["overview_issues"]) == 1
        assert ctx["overview_issues"][0]["title"] == "Convergence claim"
        # Full body, not truncated to 200 chars
        assert ctx["overview_issues"][0]["body"] == "The convergence proof has gaps."
        assert "calibration" in ctx
        assert ctx["literature_context"] == "Some lit context"
        assert ctx["section_claims"] == ["Method converges in O(n) time"]
        assert ctx["section_definitions"] == ["X := the input space"]

    def test_writes_example_output(self, tmp_path):
        agent = CodingSectionAgent(_make_config())
        section = _make_section()
        agent.prepare_workspace(
            tmp_path,
            section=section,
            paper_markdown="paper",
            all_sections=[section],
            paper_title="Test Paper",
        )
        example = json.loads((tmp_path / "example_output.json").read_text())
        assert "comments" in example
        assert len(example["comments"]) == 1
        assert "title" in example["comments"][0]

    def test_returns_task_prompt(self, tmp_path):
        agent = CodingSectionAgent(_make_config())
        section = _make_section()
        prompt = agent.prepare_workspace(
            tmp_path,
            section=section,
            paper_markdown="paper",
            all_sections=[section],
            paper_title="Test Paper",
        )
        assert "Methodology" in prompt
        assert "Test Paper" in prompt


class TestCodingSectionRun:
    """Test run() with mocked run_agent_sync."""

    @patch("coarse.agents.coding_section.run_agent_sync")
    def test_successful_run(self, mock_run):
        """Successful coding agent returns comments."""
        mock_run.return_value = _valid_section_output()
        agent = CodingSectionAgent(_make_config())
        result = agent.run(
            _make_section(), "Test Paper",
            paper_markdown="Full paper", all_sections=[_make_section()],
        )
        assert len(result) == 1
        assert result[0].title == "Test issue"
        mock_run.assert_called_once()

    @patch("coarse.agents.coding_section.run_agent_sync")
    def test_fallback_on_failure(self, mock_run):
        """RuntimeError falls back to standard SectionAgent."""
        mock_run.side_effect = RuntimeError("Agent failed")
        mock_client = MagicMock()
        mock_client.complete.return_value = _valid_section_output()

        agent = CodingSectionAgent(_make_config(), fallback_client=mock_client)
        result = agent.run(
            _make_section(), "Test Paper",
            paper_markdown="Full paper", all_sections=[_make_section()],
        )
        # Fallback should have been called
        mock_client.complete.assert_called_once()

    @patch("coarse.agents.coding_section.run_agent_sync")
    def test_no_fallback_client_reraises(self, mock_run):
        """Without fallback_client, RuntimeError propagates."""
        mock_run.side_effect = RuntimeError("Agent failed")
        agent = CodingSectionAgent(_make_config(), fallback_client=None)
        with pytest.raises(RuntimeError, match="Agent failed"):
            agent.run(
                _make_section(), "Test Paper",
                paper_markdown="Full paper", all_sections=[_make_section()],
            )

    @patch("coarse.agents.coding_section.run_agent_sync")
    def test_concurrent_agents_no_interference(self, mock_run):
        """Two concurrent coding section agents use separate temp directories."""
        mock_run.return_value = _valid_section_output()
        from concurrent.futures import ThreadPoolExecutor

        config = _make_config()
        agent = CodingSectionAgent(config)

        sections = [_make_section(1, "Methodology"), _make_section(2, "Results")]
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    agent.run, s, "Test Paper",
                    paper_markdown="paper", all_sections=sections,
                )
                for s in sections
            ]
            results = [f.result() for f in futures]

        assert len(results) == 2
        assert mock_run.call_count == 2
        # Verify they used different working directories
        calls = mock_run.call_args_list
        dir1 = calls[0].kwargs.get("working_directory") or calls[0][1][3] if len(calls[0][1]) > 3 else None
        dir2 = calls[1].kwargs.get("working_directory") or calls[1][1][3] if len(calls[1][1]) > 3 else None
        # tempfile.TemporaryDirectory creates unique dirs
        if dir1 is not None and dir2 is not None:
            assert str(dir1) != str(dir2)
