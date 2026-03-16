"""Tests for pipeline.py — review_paper orchestrator."""
from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

from coarse.config import CoarseConfig
from coarse.pipeline import (
    _compute_comment_target,
    _renumber_comments,
    _review_section,
    review_paper,
)
from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    PaperText,
    Review,
    SectionInfo,
    SectionType,
)

TEST_MODEL = "test/mock-model"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_paper_text() -> PaperText:
    return PaperText(
        full_markdown="Full paper markdown.",
        token_estimate=500,
    )


def _make_section(number: int, section_type: SectionType = SectionType.INTRODUCTION) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=f"Section {number}",
        text=f"Content of section {number}. " * 40,
        section_type=section_type,
    )


def _make_structure(sections: list[SectionInfo] | None = None) -> PaperStructure:
    if sections is None:
        sections = [_make_section(1), _make_section(2)]
    return PaperStructure(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="An abstract.",
        sections=sections,
    )


def _make_overview() -> OverviewFeedback:
    return OverviewFeedback(
        issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}.") for i in range(1, 5)]
    )


def _make_comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote="Some verbatim quote from the paper text.",
        feedback="Some feedback.",
    )


def _make_config() -> CoarseConfig:
    return CoarseConfig(default_model=TEST_MODEL)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_review_paper_calls_stages_in_order():
    """Verify each stage is called once in the correct order."""
    config = CoarseConfig(default_model=TEST_MODEL)
    paper_text = _make_paper_text()
    structure = _make_structure()
    overview = _make_overview()
    deduped = [_make_comment(1)]
    final = [_make_comment(1)]
    markdown = "# Test Paper\n"

    call_order: list[str] = []

    def fake_extract(path):
        call_order.append("extract")
        return paper_text

    def fake_analyze(pt, client):
        call_order.append("structure")
        return structure

    def fake_overview_run(s, calibration=None, literature_context=""):
        call_order.append("overview")
        return overview

    def fake_section_run(
        section, title, overview=None, calibration=None,
        focus="general", literature_context="",
        all_sections=None, abstract="",
    ):
        call_order.append(f"section_{section.number}")
        return [_make_comment(section.number)]

    def fake_crossref_run(ov, cmts, comment_target=None):
        call_order.append("crossref")
        return deduped

    def fake_critique_run(ov, cmts, comment_target=None):
        call_order.append("critique")
        return final

    def fake_render(review):
        call_order.append("render")
        return markdown

    with (
        patch("coarse.pipeline.extract_file", side_effect=fake_extract),
        patch("coarse.pipeline.analyze_structure", side_effect=fake_analyze),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CrossrefAgent") as MockCrossref,
        patch("coarse.pipeline.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", side_effect=fake_render),
    ):
        MockOverview.return_value.run_panel.side_effect = fake_overview_run
        MockSection.return_value.run.side_effect = fake_section_run
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.side_effect = fake_crossref_run
        MockCritique.return_value.run.side_effect = fake_critique_run

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert call_order[0] == "extract"
    assert call_order[1] == "structure"
    crossref_idx = call_order.index("crossref")
    critique_idx = call_order.index("critique")
    render_idx = call_order.index("render")
    assert crossref_idx < critique_idx < render_idx


def test_review_paper_skips_references_section():
    """SectionAgent.run() must not be called with the REFERENCES section."""
    config = _make_config()
    structure = _make_structure(sections=[
        _make_section(1, SectionType.INTRODUCTION),
        _make_section(2, SectionType.REFERENCES),
        _make_section(3, SectionType.CONCLUSION),
    ])
    overview = _make_overview()
    called_sections: list[SectionInfo] = []

    def fake_section_run(
        section, title, overview=None, calibration=None,
        focus="general", literature_context="",
        all_sections=None, abstract="",
    ):
        called_sections.append(section)
        return [_make_comment(section.number)]

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=structure),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CrossrefAgent") as MockCrossref,
        patch("coarse.pipeline.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run_panel.return_value = overview
        MockSection.return_value.run.side_effect = fake_section_run
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.return_value = [_make_comment(1)]
        MockCritique.return_value.run.return_value = [_make_comment(1)]

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    section_types = [s.section_type for s in called_sections]
    assert SectionType.REFERENCES not in section_types
    assert len(called_sections) == 2  # intro + conclusion


def test_review_paper_date_format():
    """Review.date must be formatted as MM/DD/YYYY."""
    config = _make_config()
    fixed_date = datetime.date(2026, 3, 3)
    overview = _make_overview()

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=_make_structure()),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CrossrefAgent") as MockCrossref,
        patch("coarse.pipeline.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
        patch("coarse.pipeline.datetime") as mock_dt,
    ):
        mock_dt.date.today.return_value = fixed_date
        MockOverview.return_value.run_panel.return_value = overview
        MockSection.return_value.run.return_value = [_make_comment(1)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.return_value = [_make_comment(1)]
        MockCritique.return_value.run.return_value = [_make_comment(1)]

        review, _, _pt = review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert review.date == "03/03/2026"


def _patch_pipeline_deps(overview: OverviewFeedback):
    """Context manager stack that stubs all pipeline dependencies."""
    from contextlib import ExitStack

    stack = ExitStack()
    stack.enter_context(patch("coarse.pipeline.extract_file", return_value=_make_paper_text()))
    stack.enter_context(patch("coarse.pipeline.analyze_structure", return_value=_make_structure()))
    stack.enter_context(patch("coarse.pipeline.calibrate_domain", return_value=None))
    stack.enter_context(patch("coarse.pipeline.search_literature", return_value=""))
    mock_ov = stack.enter_context(patch("coarse.pipeline.OverviewAgent"))
    mock_sec = stack.enter_context(patch("coarse.pipeline.SectionAgent"))
    mock_vf = stack.enter_context(patch("coarse.pipeline.ProofVerifyAgent"))
    mock_cr = stack.enter_context(patch("coarse.pipeline.CrossrefAgent"))
    mock_ct = stack.enter_context(patch("coarse.pipeline.CritiqueAgent"))
    stack.enter_context(patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c))
    stack.enter_context(patch("coarse.pipeline.render_review", return_value="md"))

    mock_ov.return_value.run_panel.return_value = overview
    mock_sec.return_value.run.return_value = [_make_comment(1)]
    mock_vf.return_value.run.return_value = [_make_comment(1)]
    mock_cr.return_value.run.return_value = [_make_comment(1)]
    mock_ct.return_value.run.return_value = [_make_comment(1)]

    return stack


def test_review_paper_skip_cost_gate():
    """run_cost_gate is only called when skip_cost_gate=False."""
    config = _make_config()
    overview = _make_overview()

    # With skip=True: run_cost_gate must NOT be called
    with patch("coarse.pipeline.run_cost_gate") as mock_gate:
        with _patch_pipeline_deps(overview):
            review_paper("paper.pdf", skip_cost_gate=True, config=config)
        mock_gate.assert_not_called()

    # With skip=False: run_cost_gate must be called
    with patch("coarse.pipeline.run_cost_gate") as mock_gate:
        with _patch_pipeline_deps(overview):
            review_paper("paper.pdf", skip_cost_gate=False, config=config)
        mock_gate.assert_called_once()


def test_review_paper_returns_review_and_markdown():
    """Return type is tuple[Review, str] with all required Review fields populated."""
    config = _make_config()
    overview = _make_overview()
    expected_markdown = "# Test Paper\n**Date**: 03/03/2026\n"

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=_make_structure()),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CrossrefAgent") as MockCrossref,
        patch("coarse.pipeline.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value=expected_markdown),
    ):
        MockOverview.return_value.run_panel.return_value = overview
        MockSection.return_value.run.return_value = [_make_comment(1)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.return_value = [_make_comment(1)]
        MockCritique.return_value.run.return_value = [_make_comment(1)]

        result = review_paper("paper.pdf", skip_cost_gate=True, config=config)

    review, markdown, _pt = result
    assert isinstance(review, Review)
    assert isinstance(markdown, str)
    assert review.title == "Test Paper"
    assert review.domain == "social_sciences/economics"
    assert review.taxonomy == "academic/research_paper"
    assert review.overall_feedback == overview
    assert markdown == expected_markdown


def test_review_paper_section_comments_flattened():
    """SectionAgent returning 2 comments per section across 3 sections → CrossrefAgent gets 6."""
    config = _make_config()
    sections = [_make_section(i) for i in range(1, 4)]
    structure = _make_structure(sections=sections)
    overview = _make_overview()

    crossref_received: list[DetailedComment] = []

    def fake_crossref_run(ov, cmts, comment_target=None):
        crossref_received.extend(cmts)
        return [_make_comment(1)]

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=structure),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CrossrefAgent") as MockCrossref,
        patch("coarse.pipeline.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run_panel.return_value = overview
        # Each section returns 2 comments
        MockSection.return_value.run.return_value = [_make_comment(1), _make_comment(2)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.side_effect = fake_crossref_run
        MockCritique.return_value.run.return_value = [_make_comment(1)]

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert len(crossref_received) == 6


def test_review_paper_uses_provided_config():
    """Provided CoarseConfig with custom model is used; load_config() is not called."""
    config = CoarseConfig(default_model="anthropic/claude-3-5-haiku-20241022")
    overview = _make_overview()
    captured_models: list[str] = []

    def fake_llm_client(model=None, config=None):
        captured_models.append(model)
        mock = MagicMock()
        return mock

    with (
        patch("coarse.pipeline.load_config") as mock_load_config,
        patch("coarse.pipeline.LLMClient", side_effect=fake_llm_client),
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=_make_structure()),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CrossrefAgent") as MockCrossref,
        patch("coarse.pipeline.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run_panel.return_value = overview
        MockSection.return_value.run.return_value = [_make_comment(1)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.return_value = [_make_comment(1)]
        MockCritique.return_value.run.return_value = [_make_comment(1)]

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    mock_load_config.assert_not_called()
    # LLMClient is called at least once for main model; vision QA may be skipped
    # if no GEMINI_API_KEY is available (e.g. in CI)
    assert captured_models[0] == "anthropic/claude-3-5-haiku-20241022"
    assert len(captured_models) >= 1


# ---------------------------------------------------------------------------
# Unit tests: _renumber_comments
# ---------------------------------------------------------------------------

def test_renumber_comments_sequential():
    """Comments get renumbered 1, 2, 3 regardless of input numbers."""
    comments = [
        _make_comment(5),
        _make_comment(10),
        _make_comment(3),
    ]
    result = _renumber_comments(comments)
    assert [c.number for c in result] == [1, 2, 3]


def test_renumber_comments_preserves_content():
    """Renumbering only changes .number, not other fields."""
    comment = DetailedComment(
        number=99, title="Test",
        quote="Verbatim quote from the paper.",
        feedback="f", severity="critical",
    )
    result = _renumber_comments([comment])
    assert result[0].number == 1
    assert result[0].title == "Test"
    assert result[0].severity == "critical"


def test_renumber_comments_empty():
    assert _renumber_comments([]) == []


# ---------------------------------------------------------------------------
# Unit tests: _compute_comment_target
# ---------------------------------------------------------------------------

def test_compute_comment_target_small_paper():
    """Small paper (2 sections, 500 tokens) → clamped to minimum 6."""
    structure = _make_structure(sections=[_make_section(1), _make_section(2)])
    paper_text = PaperText(full_markdown="short", token_estimate=500)
    target = _compute_comment_target(structure, paper_text)
    assert target == 6  # 2*1.5 + 0.5*0.3 = 3.15 → clamped to 6


def test_compute_comment_target_large_paper():
    """Large paper (15 sections, 30K tokens) → reasonable target."""
    sections = [_make_section(i) for i in range(1, 16)]
    structure = _make_structure(sections=sections)
    paper_text = PaperText(full_markdown="x" * 100000, token_estimate=30000)
    target = _compute_comment_target(structure, paper_text)
    # 15*1.5 + 30*0.3 = 22.5 + 9 = 31.5 → clamped to 25
    assert target == 25


def test_compute_comment_target_medium_paper():
    """Medium paper (6 sections, 10K tokens)."""
    sections = [_make_section(i) for i in range(1, 7)]
    structure = _make_structure(sections=sections)
    paper_text = PaperText(full_markdown="x" * 30000, token_estimate=10000)
    target = _compute_comment_target(structure, paper_text)
    # 6*1.5 + 10*0.3 = 9 + 3 = 12
    assert target == 12


def test_compute_comment_target_excludes_references():
    """References and appendix sections don't count toward section count."""
    sections = [
        _make_section(1, SectionType.INTRODUCTION),
        _make_section(2, SectionType.METHODOLOGY),
        _make_section(3, SectionType.REFERENCES),
        _make_section(4, SectionType.APPENDIX),
    ]
    structure = _make_structure(sections=sections)
    paper_text = PaperText(full_markdown="x" * 10000, token_estimate=5000)
    target = _compute_comment_target(structure, paper_text)
    # 2 reviewable sections * 1.5 + 5*0.3 = 3 + 1.5 = 4.5 → clamped to 6
    assert target == 6


# ---------------------------------------------------------------------------
# _review_section + appendix filter tests
# ---------------------------------------------------------------------------

def test_review_section_chains_verify_for_proof():
    """_review_section with focus='proof' calls both section agent and verify agent."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    section = _make_section(1)
    first_pass = [_make_comment(1)]
    verified = [_make_comment(1), _make_comment(2)]

    section_agent.run.return_value = first_pass
    verify_agent.run.return_value = verified

    result = _review_section(
        section_agent, verify_agent, section, "Paper",
        overview=None, calibration=None, focus="proof",
        literature_context="", all_sections=[], abstract="abstract",
    )

    section_agent.run.assert_called_once()
    verify_agent.run.assert_called_once_with(
        section, "Paper", first_pass, abstract="abstract",
    )
    assert result == verified


def test_review_section_skips_verify_for_non_proof():
    """_review_section with focus='general' only calls section agent."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    section = _make_section(1)
    comments = [_make_comment(1)]
    section_agent.run.return_value = comments

    result = _review_section(
        section_agent, verify_agent, section, "Paper",
        overview=None, calibration=None, focus="general",
        literature_context="", all_sections=[], abstract="",
    )

    section_agent.run.assert_called_once()
    verify_agent.run.assert_not_called()
    assert result == comments


def test_appendix_filter_includes_long_appendix():
    """Appendix with >= 500 chars is included in reviewable sections."""
    appendix = SectionInfo(
        number="A",
        title="Robustness Checks",
        text="x" * 600,
        section_type=SectionType.APPENDIX,
    )
    sections = [_make_section(1), appendix]
    structure = _make_structure(sections=sections)

    # Replicate the pipeline's filter logic
    _MIN_APPENDIX_CHARS = 500
    reviewable = [
        s for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX
             or len(s.text) >= _MIN_APPENDIX_CHARS)
    ]
    assert appendix in reviewable


def test_appendix_filter_skips_short_appendix():
    """Appendix with < 500 chars is excluded from reviewable sections."""
    appendix = SectionInfo(
        number="A",
        title="Short Appendix",
        text="x" * 100,
        section_type=SectionType.APPENDIX,
    )
    sections = [_make_section(1), appendix]
    structure = _make_structure(sections=sections)

    _MIN_APPENDIX_CHARS = 500
    reviewable = [
        s for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX
             or len(s.text) >= _MIN_APPENDIX_CHARS)
    ]
    assert appendix not in reviewable
