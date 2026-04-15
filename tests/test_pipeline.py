"""Tests for pipeline.py — review_paper orchestrator."""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

from coarse.config import CoarseConfig
from coarse.pipeline import (
    _renumber_comments,
    _review_section,
    _section_needs_proof_verify,
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


def _make_section(
    number: int,
    section_type: SectionType = SectionType.INTRODUCTION,
    text: str | None = None,
    math_content: bool = False,
) -> SectionInfo:
    return SectionInfo(
        number=number,
        title=f"Section {number}",
        text=text if text is not None else f"Content of section {number}. " * 40,
        section_type=section_type,
        math_content=math_content,
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
    markdown = "# Test Paper\n"

    call_order: list[str] = []

    def fake_extract(path):
        call_order.append("extract")
        return paper_text

    def fake_analyze(pt, client):
        call_order.append("structure")
        return structure

    def fake_overview_run(s, calibration=None, literature_context="", author_notes=None):
        call_order.append("overview")
        return overview

    def fake_section_run(
        section,
        title,
        overview=None,
        calibration=None,
        focus="general",
        literature_context="",
        all_sections=None,
        abstract="",
        document_form="manuscript",
        author_notes=None,
    ):
        call_order.append(f"section_{section.number}")
        return [_make_comment(section.number)]

    def fake_completeness_run(
        structure,
        overview,
        calibration=None,
        contribution_context=None,
        author_notes=None,
    ):
        call_order.append("completeness")
        return []

    def fake_editorial_run(
        paper_text,
        overview,
        comments,
        comment_target=None,
        title="",
        abstract="",
        contribution_context=None,
        document_form="manuscript",
        author_notes=None,
    ):
        call_order.append("editorial")
        return [_make_comment(1)]

    def fake_render(review):
        call_order.append("render")
        return markdown

    with (
        patch("coarse.pipeline.extract_file", side_effect=fake_extract),
        patch("coarse.pipeline.analyze_structure", side_effect=fake_analyze),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.extract_contribution", return_value=None),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.CompletenessAgent") as MockCompleteness,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", side_effect=fake_render),
    ):
        MockOverview.return_value.run.side_effect = fake_overview_run
        MockCompleteness.return_value.run.side_effect = fake_completeness_run
        MockSection.return_value.run.side_effect = fake_section_run
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockEditorial.return_value.run.side_effect = fake_editorial_run

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert call_order[0] == "extract"
    assert call_order[1] == "structure"
    overview_idx = call_order.index("overview")
    completeness_idx = call_order.index("completeness")
    editorial_idx = call_order.index("editorial")
    render_idx = call_order.index("render")
    assert overview_idx < completeness_idx < editorial_idx < render_idx


def test_review_paper_skips_references_section():
    """SectionAgent.run() must not be called with the REFERENCES section."""
    config = _make_config()
    structure = _make_structure(
        sections=[
            _make_section(1, SectionType.INTRODUCTION),
            _make_section(2, SectionType.REFERENCES),
            _make_section(3, SectionType.CONCLUSION),
        ]
    )
    overview = _make_overview()
    called_sections: list[SectionInfo] = []

    def fake_section_run(
        section,
        title,
        overview=None,
        calibration=None,
        focus="general",
        literature_context="",
        all_sections=None,
        abstract="",
        document_form="manuscript",
        author_notes=None,
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
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run.return_value = overview
        MockSection.return_value.run.side_effect = fake_section_run
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCrossref.return_value.run.return_value = [_make_comment(1)]
        MockCritique.return_value.run.return_value = [_make_comment(1)]

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    section_types = [s.section_type for s in called_sections]
    assert SectionType.REFERENCES not in section_types
    assert len(called_sections) == 2  # intro + conclusion


def test_review_paper_forwards_author_notes_to_all_review_agents():
    """review_paper(author_notes=...) must forward the notes to every review
    pass that can shape user-visible output."""
    config = _make_config()
    structure = _make_structure(
        sections=[
            _make_section(1, SectionType.INTRODUCTION, text="Intro text."),
            _make_section(
                2,
                SectionType.METHODOLOGY,
                text="Theorem 1. " + ("formal proof text " * 80),
                math_content=True,
            ),
            _make_section(
                3,
                SectionType.DISCUSSION,
                text="Discussion text tying policy claims to the theorem.",
            ),
        ]
    )
    overview = _make_overview()

    captured: dict[str, object] = {}

    def capture_overview(s, calibration=None, literature_context="", author_notes=None):
        captured["overview_notes"] = author_notes
        return overview

    def capture_section(
        section,
        title,
        overview=None,
        calibration=None,
        focus="general",
        literature_context="",
        all_sections=None,
        abstract="",
        document_form="manuscript",
        author_notes=None,
    ):
        captured.setdefault("section_notes", []).append(author_notes)  # type: ignore[union-attr]
        return [_make_comment(section.number)]

    def capture_verify(
        section,
        title,
        comments,
        abstract="",
        document_form="manuscript",
        author_notes=None,
    ):
        captured.setdefault("verify_notes", []).append(author_notes)  # type: ignore[union-attr]
        return comments

    def capture_completeness(
        structure_arg,
        overview_arg,
        calibration=None,
        contribution_context=None,
        author_notes=None,
    ):
        captured["completeness_notes"] = author_notes
        return []

    def capture_cross_section(
        title,
        results_section,
        discussion_section,
        abstract="",
        document_form="manuscript",
        author_notes=None,
    ):
        captured.setdefault("cross_section_notes", []).append(author_notes)  # type: ignore[union-attr]
        return []

    def capture_editorial(
        paper_text,
        overview_arg,
        comments,
        comment_target=None,
        title="",
        abstract="",
        contribution_context=None,
        document_form="manuscript",
        author_notes=None,
    ):
        captured["editorial_notes"] = author_notes
        return comments

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=structure),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.extract_contribution", return_value=None),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CompletenessAgent") as MockCompleteness,
        patch("coarse.pipeline.CrossSectionAgent") as MockCrossSection,
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run.side_effect = capture_overview
        MockSection.return_value.run.side_effect = capture_section
        MockVerify.return_value.run.side_effect = capture_verify
        MockCompleteness.return_value.run.side_effect = capture_completeness
        MockCrossSection.return_value.run.side_effect = capture_cross_section
        MockEditorial.return_value.run.side_effect = capture_editorial

        review_paper(
            "paper.pdf",
            skip_cost_gate=True,
            config=config,
            author_notes="please focus on the identification strategy",
        )

    assert captured["overview_notes"] == "please focus on the identification strategy"
    assert captured["completeness_notes"] == "please focus on the identification strategy"
    assert captured["editorial_notes"] == "please focus on the identification strategy"
    assert captured["verify_notes"] == ["please focus on the identification strategy"]
    assert captured["cross_section_notes"] == ["please focus on the identification strategy"]
    assert captured["section_notes"] == [
        "please focus on the identification strategy",
        "please focus on the identification strategy",
        "please focus on the identification strategy",
    ]


def test_review_paper_forwards_author_notes_to_fallback_crossref_and_critique():
    config = _make_config()
    structure = _make_structure(
        sections=[
            _make_section(1, SectionType.INTRODUCTION),
            _make_section(2, SectionType.METHODOLOGY),
        ]
    )
    overview = _make_overview()
    captured: dict[str, object] = {}

    def capture_crossref(
        overview_arg,
        comments,
        comment_target=None,
        title="",
        abstract="",
        author_notes=None,
    ):
        captured["crossref_notes"] = author_notes
        return comments

    def capture_critique(
        overview_arg,
        comments,
        comment_target=None,
        title="",
        abstract="",
        author_notes=None,
    ):
        captured["critique_notes"] = author_notes
        return comments

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=structure),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.extract_contribution", return_value=None),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CompletenessAgent") as MockCompleteness,
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run.return_value = overview
        MockSection.return_value.run.return_value = [_make_comment(1)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCompleteness.return_value.run.return_value = []
        MockEditorial.return_value.run.side_effect = RuntimeError("editorial boom")
        MockCrossref.return_value.run.side_effect = capture_crossref
        MockCritique.return_value.run.side_effect = capture_critique

        review_paper(
            "paper.pdf",
            skip_cost_gate=True,
            config=config,
            author_notes="please focus on the identification strategy",
        )

    assert captured["crossref_notes"] == "please focus on the identification strategy"
    assert captured["critique_notes"] == "please focus on the identification strategy"


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
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
        patch("coarse.pipeline.datetime") as mock_dt,
    ):
        mock_dt.date.today.return_value = fixed_date
        MockOverview.return_value.run.return_value = overview
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
    mock_cr = stack.enter_context(patch("coarse.review_stages.CrossrefAgent"))
    mock_ct = stack.enter_context(patch("coarse.review_stages.CritiqueAgent"))
    stack.enter_context(patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c))
    stack.enter_context(patch("coarse.pipeline.render_review", return_value="md"))

    mock_ov.return_value.run.return_value = overview
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
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value=expected_markdown),
    ):
        MockOverview.return_value.run.return_value = overview
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

    editorial_received: list[DetailedComment] = []

    def fake_editorial_run(
        paper_text,
        overview,
        comments,
        comment_target=None,
        title="",
        abstract="",
        contribution_context=None,
        document_form="manuscript",
        author_notes=None,
    ):
        editorial_received.extend(comments)
        return [_make_comment(1)]

    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=structure),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.extract_contribution", return_value=None),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.CompletenessAgent") as MockCompleteness,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run.return_value = overview
        MockCompleteness.return_value.run.return_value = []
        # Each section returns 2 comments
        MockSection.return_value.run.return_value = [_make_comment(1), _make_comment(2)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockEditorial.return_value.run.side_effect = fake_editorial_run

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert len(editorial_received) == 6


def test_review_paper_verifies_section_quotes_before_editorial_handoff():
    """Editorial should receive the quote-verified section comments rather than
    the raw LLM output from section agents."""
    config = _make_config()
    structure = _make_structure(sections=[_make_section(1), _make_section(2)])
    overview = _make_overview()
    editorial_received: list[DetailedComment] = []

    def fake_verify(comments, _paper_text, drop_unverified=True):
        return [c.model_copy(update={"quote": f"verified: {c.quote}"}) for c in comments]

    def fake_editorial_run(
        paper_text,
        overview,
        comments,
        comment_target=None,
        title="",
        abstract="",
        contribution_context=None,
        document_form="manuscript",
        author_notes=None,
    ):
        editorial_received.extend(comments)
        return comments

    # Patch targets live on `coarse.review_stages` after the pipeline
    # refactor (#87) — EditorialAgent, _review_section, calibrate_domain,
    # extract_contribution, and verify_quotes all resolved in that module's
    # namespace at import time, and pipeline.py just re-imports the
    # helpers. Patching `coarse.pipeline.X` for these would no-op against
    # the call sites inside review_stages.
    with (
        patch("coarse.pipeline.extract_file", return_value=_make_paper_text()),
        patch("coarse.pipeline.analyze_structure", return_value=structure),
        patch("coarse.review_stages.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.review_stages.extract_contribution", return_value=None),
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.CompletenessAgent") as MockCompleteness,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.review_stages.verify_quotes", side_effect=fake_verify),
        patch("coarse.pipeline.verify_quotes", side_effect=fake_verify),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run.return_value = overview
        MockCompleteness.return_value.run.return_value = []
        MockSection.return_value.run.return_value = [_make_comment(1)]
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockEditorial.return_value.run.side_effect = fake_editorial_run

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert editorial_received
    assert all(comment.quote.startswith("verified: ") for comment in editorial_received)


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
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
        patch("coarse.pipeline.verify_quotes", side_effect=lambda c, t, **kw: c),
        patch("coarse.pipeline.render_review", return_value="md"),
    ):
        MockOverview.return_value.run.return_value = overview
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
        number=99,
        title="Test",
        quote="Verbatim quote from the paper.",
        feedback="f",
        severity="critical",
    )
    result = _renumber_comments([comment])
    assert result[0].number == 1
    assert result[0].title == "Test"
    assert result[0].severity == "critical"


def test_renumber_comments_empty():
    assert _renumber_comments([]) == []


# ---------------------------------------------------------------------------
# _review_section + appendix filter tests
# ---------------------------------------------------------------------------


def test_review_section_chains_verify_for_proof():
    """_review_section with focus='proof' + math_content + long text calls both agents."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    # _make_section produces text="Content of section 1. " * 40 ≈ 800 chars,
    # so it passes the proof_verify length threshold. Set math_content=True
    # because the threshold now requires the LLM-detected flag too.
    section = _make_section(1).model_copy(update={"math_content": True})
    first_pass = [_make_comment(1)]
    verified = [_make_comment(1), _make_comment(2)]

    section_agent.run.return_value = first_pass
    verify_agent.run.return_value = verified

    result = _review_section(
        section_agent,
        verify_agent,
        section,
        "Some verbatim quote from the paper text.",
        "Paper",
        overview=None,
        calibration=None,
        focus="proof",
        literature_context="",
        all_sections=[],
        abstract="abstract",
    )

    section_agent.run.assert_called_once()
    verify_agent.run.assert_called_once_with(
        section,
        "Paper",
        first_pass,
        abstract="abstract",
        document_form="manuscript",
        author_notes=None,
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
        section_agent,
        verify_agent,
        section,
        "Some verbatim quote from the paper text.",
        "Paper",
        overview=None,
        calibration=None,
        focus="general",
        literature_context="",
        all_sections=[],
        abstract="",
    )

    section_agent.run.assert_called_once()
    verify_agent.run.assert_not_called()
    assert result == comments


def test_review_section_verifies_quotes_before_verify_and_on_return():
    """Proof verification should receive verified first-pass comments, and
    the returned comments should also be re-verified before leaving the helper."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    section = _make_section(1).model_copy(update={"math_content": True})
    first_pass = [_make_comment(1)]
    verified_pass = [_make_comment(2)]

    section_agent.run.return_value = first_pass
    verify_agent.run.return_value = verified_pass

    call_count = {"n": 0}

    drop_flags: list[bool] = []

    def fake_verify(comments, _paper_text, drop_unverified=True):
        drop_flags.append(drop_unverified)
        call_count["n"] += 1
        prefix = f"verified-{call_count['n']}"
        return [c.model_copy(update={"quote": f"{prefix}: {c.quote}"}) for c in comments]

    # _review_section lives in coarse.review_stages after the pipeline
    # refactor (#87), and that's where `verify_quotes` is imported at
    # module load time. Patching `coarse.pipeline.verify_quotes` no-ops
    # against the helper's actual lookup.
    with patch("coarse.review_stages.verify_quotes", side_effect=fake_verify):
        result = _review_section(
            section_agent,
            verify_agent,
            section,
            "Full paper markdown.",
            "Paper",
            overview=None,
            calibration=None,
            focus="proof",
            literature_context="",
            all_sections=[],
            abstract="abstract",
        )

    verify_agent.run.assert_called_once()
    verify_input = verify_agent.run.call_args.args[2]
    assert drop_flags == [False, False]
    assert verify_input[0].quote.startswith("verified-1:")
    assert result[0].quote.startswith("verified-2:")


def test_review_section_marks_approximate_quotes_instead_of_dropping_them():
    """Intermediate verification should preserve recall by keeping comments
    and marking their quotes approximate instead of dropping them."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    section = _make_section(1)
    comments = [_make_comment(1)]
    section_agent.run.return_value = comments

    approximate = comments[0].model_copy(update={"quote": "[approximate] " + comments[0].quote})

    def fake_verify(_comments, _paper_text, drop_unverified=True):
        assert drop_unverified is False
        return [approximate]

    with patch("coarse.review_stages.verify_quotes", side_effect=fake_verify):
        result = _review_section(
            section_agent,
            verify_agent,
            section,
            "Full paper markdown.",
            "Paper",
            overview=None,
            calibration=None,
            focus="general",
            literature_context="",
            all_sections=[],
            abstract="",
        )

    verify_agent.run.assert_not_called()
    assert result == [approximate]


# ---------------------------------------------------------------------------
# _section_needs_proof_verify — threshold gates trivial math sections
# ---------------------------------------------------------------------------


def _math_section(text: str, claims: list[str] | None = None) -> SectionInfo:
    return SectionInfo(
        number=1,
        title="Section 1",
        text=text,
        section_type=SectionType.METHODOLOGY,
        math_content=True,
        claims=claims or [],
    )


def test_section_needs_proof_verify_requires_math_content_flag():
    """Without the LLM-set math_content flag, proof_verify never runs even
    if the section has formal-looking structure — the flag IS the signal."""
    section = SectionInfo(
        number=1,
        title="Section 1",
        text="x" * 2000,
        section_type=SectionType.METHODOLOGY,
        math_content=False,
    )
    assert _section_needs_proof_verify(section) is False


def test_section_needs_proof_verify_short_section_with_formal_claim():
    """A short section that contains an extracted formal claim is verified
    regardless of length. This covers the short-lemma-with-proof case —
    a 250-char "Lemma 1: X. Proof: Y." paragraph still deserves adversarial
    verification because the paper explicitly marked it as a formal result.
    """
    section = _math_section(
        text="Lemma 1: Every P is Q. Proof: By induction on n.",
        claims=["Lemma 1: Every P is Q"],
    )
    assert len(section.text) < 500
    assert _section_needs_proof_verify(section) is True


def test_section_needs_proof_verify_long_section_without_claims():
    """A section with math_content=True but no extracted claims still
    passes the gate as long as it's long enough to contain meaningful
    math content (>=500 chars)."""
    section = _math_section(text="x" * 600)
    assert _section_needs_proof_verify(section) is True


def test_section_needs_proof_verify_short_section_without_claims_skipped():
    """A math-flagged section that's too short and has no extracted
    formal claims is skipped. This is the case the threshold is meant to
    filter: a discussion section with one inline equation in a footnote
    isn't worth a full proof_verify call."""
    section = _math_section(text="The value x = 42 is notable.", claims=[])
    assert len(section.text) < 500
    assert _section_needs_proof_verify(section) is False


def test_review_section_skips_verify_when_threshold_fails():
    """_review_section with focus='proof' but a short math-flagged section
    that has no formal claims must NOT call verify_agent — the threshold
    gate at _section_needs_proof_verify filters it out."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    # Short section (~30 chars), math_content flagged, no claims → skip
    section = SectionInfo(
        number=1,
        title="Section 1",
        text="The value x = 42 is notable.",
        section_type=SectionType.METHODOLOGY,
        math_content=True,
    )
    first_pass = [_make_comment(1)]
    section_agent.run.return_value = first_pass

    result = _review_section(
        section_agent,
        verify_agent,
        section,
        "Some verbatim quote from the paper text.",
        "Paper",
        overview=None,
        calibration=None,
        focus="proof",
        literature_context="",
        all_sections=[],
        abstract="abstract",
    )

    section_agent.run.assert_called_once()
    verify_agent.run.assert_not_called()
    assert result == first_pass


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
        s
        for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX or len(s.text) >= _MIN_APPENDIX_CHARS)
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
        s
        for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX or len(s.text) >= _MIN_APPENDIX_CHARS)
    ]
    assert appendix not in reviewable
