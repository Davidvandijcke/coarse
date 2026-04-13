"""Tests for pipeline.py — review_paper orchestrator."""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

from coarse.config import CoarseConfig
from coarse.pipeline import (
    _renumber_comments,
    _repair_quotes_with_agent,
    _review_section,
    _verify_section_with_fallback,
    _verify_with_repair_fallback,
    review_paper,
)
from coarse.quote_verify import QuoteVerificationDrop, QuoteVerificationResult
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


def _make_comment(number: int = 1, quote: str | None = None) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote=quote or "Some verbatim quote from the paper text.",
        feedback="Some feedback.",
    )


def _make_config() -> CoarseConfig:
    return CoarseConfig(default_model=TEST_MODEL)


def _patch_review_paper_deps(
    *,
    structure: PaperStructure | None = None,
    overview: OverviewFeedback | None = None,
    editorial_comments: list[DetailedComment] | None = None,
) -> tuple[object, dict[str, MagicMock]]:
    """Patch the review_paper dependency graph and return (stack, mocks)."""
    from contextlib import ExitStack

    structure = structure or _make_structure()
    overview = overview or _make_overview()
    editorial_comments = editorial_comments or [_make_comment(1)]

    stack = ExitStack()
    stack.enter_context(patch("coarse.pipeline.extract_file", return_value=_make_paper_text()))
    stack.enter_context(patch("coarse.pipeline.analyze_structure", return_value=structure))
    stack.enter_context(patch("coarse.pipeline.calibrate_domain", return_value=None))
    stack.enter_context(patch("coarse.pipeline.search_literature", return_value=""))
    stack.enter_context(patch("coarse.pipeline.extract_contribution", return_value=None))
    stack.enter_context(
        patch(
            "coarse.pipeline._verify_with_repair_fallback",
            side_effect=lambda comments, paper_text, repair_agent=None: comments,
        )
    )
    stack.enter_context(patch("coarse.pipeline.render_review", return_value="md"))

    mock_router_cls = stack.enter_context(patch("coarse.pipeline.StageRouter"))
    mock_overview_cls = stack.enter_context(patch("coarse.pipeline.OverviewAgent"))
    mock_section_cls = stack.enter_context(patch("coarse.pipeline.SectionAgent"))
    mock_verify_cls = stack.enter_context(patch("coarse.pipeline.ProofVerifyAgent"))
    mock_completeness_cls = stack.enter_context(patch("coarse.pipeline.CompletenessAgent"))
    mock_editorial_cls = stack.enter_context(patch("coarse.pipeline.EditorialAgent"))
    mock_quote_repair_cls = stack.enter_context(patch("coarse.pipeline.QuoteRepairAgent"))

    mock_router = mock_router_cls.return_value
    mock_router.client_for.side_effect = lambda stage: MagicMock(name=f"{stage}_client")

    mock_overview = mock_overview_cls.return_value
    mock_section = mock_section_cls.return_value
    mock_verify = mock_verify_cls.return_value
    mock_completeness = mock_completeness_cls.return_value
    mock_editorial = mock_editorial_cls.return_value
    mock_quote_repair = mock_quote_repair_cls.return_value

    mock_overview.run.return_value = overview
    mock_section.run.return_value = [_make_comment(1)]
    mock_verify.run.return_value = [_make_comment(1)]
    mock_completeness.run.return_value = []
    mock_editorial.run.return_value = editorial_comments
    mock_quote_repair.run.return_value = {}

    mocks = {
        "router_cls": mock_router_cls,
        "router": mock_router,
        "overview_cls": mock_overview_cls,
        "overview": mock_overview,
        "section_cls": mock_section_cls,
        "section": mock_section,
        "verify": mock_verify,
        "editorial": mock_editorial,
        "quote_repair": mock_quote_repair,
    }
    return stack, mocks


def test_review_paper_calls_stages_in_order():
    """Verify extraction, overview, sections, editorial, and render all execute."""
    config = _make_config()
    structure = _make_structure()
    overview = _make_overview()
    call_order: list[str] = []

    def fake_extract(path):
        call_order.append("extract")
        return _make_paper_text()

    def fake_analyze(pt, metadata_client, math_client=None):
        call_order.append("structure")
        return structure

    def fake_overview_run(s, calibration=None, literature_context=""):
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
    ):
        call_order.append(f"section_{section.number}")
        return [_make_comment(section.number)]

    def fake_editorial_run(
        paper_text,
        overview,
        comments,
        comment_target=None,
        title="",
        abstract="",
        contribution_context=None,
        document_form="manuscript",
    ):
        call_order.append("editorial")
        return comments

    with (
        patch("coarse.pipeline.extract_file", side_effect=fake_extract),
        patch("coarse.pipeline.analyze_structure", side_effect=fake_analyze),
        patch("coarse.pipeline.calibrate_domain", return_value=None),
        patch("coarse.pipeline.search_literature", return_value=""),
        patch("coarse.pipeline.extract_contribution", return_value=None),
        patch(
            "coarse.pipeline._verify_with_repair_fallback",
            side_effect=lambda comments, paper_text, repair_agent=None: comments,
        ),
        patch(
            "coarse.pipeline.render_review",
            side_effect=lambda review: call_order.append("render") or "md",
        ),
        patch("coarse.pipeline.StageRouter") as MockRouter,
        patch("coarse.pipeline.OverviewAgent") as MockOverview,
        patch("coarse.pipeline.SectionAgent") as MockSection,
        patch("coarse.pipeline.ProofVerifyAgent") as MockVerify,
        patch("coarse.pipeline.CompletenessAgent") as MockCompleteness,
        patch("coarse.pipeline.EditorialAgent") as MockEditorial,
        patch("coarse.pipeline.QuoteRepairAgent"),
    ):
        MockRouter.return_value.client_for.side_effect = lambda stage: MagicMock(name=stage)
        MockOverview.return_value.run.side_effect = fake_overview_run
        MockSection.return_value.run.side_effect = fake_section_run
        MockVerify.return_value.run.return_value = [_make_comment(1)]
        MockCompleteness.return_value.run.return_value = []
        MockEditorial.return_value.run.side_effect = fake_editorial_run

        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert call_order[0] == "extract"
    assert call_order[1] == "structure"
    assert call_order[2] == "overview"
    assert "editorial" in call_order
    assert call_order[-1] == "render"


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
    ):
        called_sections.append(section)
        return [_make_comment(section.number)]

    stack, mocks = _patch_review_paper_deps(structure=structure)
    with stack:
        mocks["section"].run.side_effect = fake_section_run
        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    section_types = [s.section_type for s in called_sections]
    assert SectionType.REFERENCES not in section_types
    assert len(called_sections) == 2


def test_review_paper_date_format():
    """Review.date must be formatted as MM/DD/YYYY."""
    config = _make_config()
    fixed_date = datetime.date(2026, 3, 3)

    stack, _mocks = _patch_review_paper_deps()
    with stack, patch("coarse.pipeline.datetime") as mock_dt:
        mock_dt.date.today.return_value = fixed_date
        review, _, _pt = review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert review.date == "03/03/2026"


def test_review_paper_skip_cost_gate():
    """run_cost_gate is only called when skip_cost_gate=False."""
    config = _make_config()

    with patch("coarse.pipeline.run_cost_gate") as mock_gate:
        stack, _mocks = _patch_review_paper_deps()
        with stack:
            review_paper("paper.pdf", skip_cost_gate=True, config=config)
        mock_gate.assert_not_called()

    with patch("coarse.pipeline.run_cost_gate") as mock_gate:
        stack, _mocks = _patch_review_paper_deps()
        with stack:
            review_paper("paper.pdf", skip_cost_gate=False, config=config)
        mock_gate.assert_called_once()


def test_review_paper_returns_review_and_markdown():
    """Return type is tuple[Review, str] with required Review fields populated."""
    config = _make_config()
    overview = _make_overview()
    expected_markdown = "# Test Paper\n**Date**: 03/03/2026\n"

    stack, _mocks = _patch_review_paper_deps(overview=overview)
    with stack, patch("coarse.pipeline.render_review", return_value=expected_markdown):
        review, markdown, _pt = review_paper("paper.pdf", skip_cost_gate=True, config=config)

    assert isinstance(review, Review)
    assert isinstance(markdown, str)
    assert review.title == "Test Paper"
    assert review.domain == "social_sciences/economics"
    assert review.taxonomy == "academic/research_paper"
    assert review.overall_feedback == overview
    assert markdown == expected_markdown


def test_review_paper_uses_provided_config():
    """Provided CoarseConfig custom model is routed into StageRouter."""
    config = CoarseConfig(default_model="anthropic/claude-3-5-haiku-20241022")

    stack, mocks = _patch_review_paper_deps()
    with stack:
        review_paper("paper.pdf", skip_cost_gate=True, config=config)

    mocks["router_cls"].assert_called_once()
    assert (
        mocks["router_cls"].call_args.kwargs["base_model"] == "anthropic/claude-3-5-haiku-20241022"
    )


def test_renumber_comments_sequential():
    """Comments get renumbered 1, 2, 3 regardless of input numbers."""
    comments = [_make_comment(5), _make_comment(10), _make_comment(3)]
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


def test_review_section_chains_verify_for_proof():
    """_review_section with focus='proof' calls both section and verify agents."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    section = _make_section(1).model_copy(update={"math_content": True})
    first_pass = [_make_comment(1)]
    verified = [_make_comment(1), _make_comment(2)]

    section_agent.run.return_value = first_pass
    verify_agent.run.return_value = verified

    result = _review_section(
        section_agent,
        verify_agent,
        section,
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


def test_review_section_runs_section_local_quote_verification():
    """Section-local verification should correct harmless formatting drift."""
    section_agent = MagicMock()
    verify_agent = MagicMock()
    section = SectionInfo(
        number=1,
        title="Introduction",
        text=(
            "For large budgets, optimal interventions are simple — they involve a single "
            "principal component."
        ),
        section_type=SectionType.INTRODUCTION,
    )
    section_agent.run.return_value = [
        DetailedComment(
            number=1,
            title="Budget concentration claim",
            quote=(
                "For large budgets, optimal interventions are simple - they involve a single "
                "principal component."
            ),
            feedback="Feedback.",
        )
    ]

    result = _review_section(
        section_agent,
        verify_agent,
        section,
        "Paper",
        overview=None,
        calibration=None,
        focus="general",
        literature_context="",
        all_sections=[],
        abstract="",
    )

    assert result[0].quote == section.text


def test_verify_section_with_fallback_keeps_originals_if_all_dropped():
    """Section-local verification must fail open rather than erase comments."""
    section = SectionInfo(
        number=1,
        title="Introduction",
        text="This section has unrelated text only.",
        section_type=SectionType.INTRODUCTION,
    )
    comments = [
        DetailedComment(
            number=1,
            title="Unmatched quote",
            quote="A sufficiently long quote that is not present in the section text.",
            feedback="Feedback.",
        )
    ]

    result = _verify_section_with_fallback(comments, section)
    assert result == comments


def test_repair_quotes_with_agent_reverifies_before_salvage():
    """Repaired quotes only survive if deterministic re-verification accepts them."""
    comment = DetailedComment(
        number=3,
        title="Repair me",
        quote="Original long quote that missed slightly.",
        feedback="Feedback.",
    )
    dropped = [
        QuoteVerificationDrop(
            comment=comment,
            ratio=0.74,
            threshold=0.80,
            candidate_passages=["Correct repaired quote from the paper."],
        )
    ]
    repair_agent = MagicMock()
    repair_agent.run.return_value = {3: "Correct repaired quote from the paper."}

    repaired = _repair_quotes_with_agent(
        dropped,
        "Prefix. Correct repaired quote from the paper. Suffix.",
        repair_agent,
    )

    assert len(repaired) == 1
    assert repaired[0].quote == "Correct repaired quote from the paper."


def test_verify_with_repair_fallback_merges_salvaged_comments_in_order():
    """Salvaged comments should be reinserted in original comment order."""
    kept = DetailedComment(
        number=1,
        title="Kept",
        quote="Exact match from paper.",
        feedback="Feedback.",
    )
    dropped = DetailedComment(
        number=2,
        title="Dropped",
        quote="Recovered anchor from paper -",
        feedback="Feedback.",
    )
    repair_agent = MagicMock()
    repair_agent.run.return_value = {2: "Recovered anchor from paper."}

    verification = QuoteVerificationResult(
        verified_comments=[kept],
        dropped_comments=[
            QuoteVerificationDrop(
                comment=dropped,
                ratio=0.74,
                threshold=0.80,
                candidate_passages=["Recovered anchor from paper."],
            )
        ],
        stats={"exact": 1, "fuzzy": 0, "dropped": 1, "empty": 0, "garbled_source": 0},
    )

    with (
        patch("coarse.pipeline.verify_quotes_detailed", return_value=verification),
        patch(
            "coarse.pipeline.verify_quotes",
            return_value=[dropped.model_copy(update={"quote": "Recovered anchor from paper."})],
        ),
    ):
        result = _verify_with_repair_fallback(
            [kept, dropped],
            "Exact match from paper.\nRecovered anchor from paper.\n",
            repair_agent=repair_agent,
        )

    assert [c.number for c in result] == [1, 2]
    assert result[1].quote == "Recovered anchor from paper."


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

    reviewable = [
        s
        for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX or len(s.text) >= 500)
    ]
    assert appendix not in reviewable
