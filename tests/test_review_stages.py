"""Tests for coarse.review_stages."""

from __future__ import annotations

from unittest.mock import Mock, patch

from coarse.review_stages import (
    _MAX_FINAL_COMMENTS,
    _cap_comments,
    _detect_section_focus,
    _review_section,
    calibrate_domain,
    extract_contribution,
    run_editorial_pass,
)
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, SectionInfo, SectionType


def _comment(number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title=f"Comment {number}",
        quote="This is a sufficiently long quote from the paper.",
        feedback="This is detailed feedback.",
    )


def _overview() -> OverviewFeedback:
    return OverviewFeedback(
        summary="",
        issues=[OverviewIssue(title="Issue", body="Body")],
    )


def test_detect_section_focus_routes_common_section_types():
    assert (
        _detect_section_focus(
            SectionInfo(number=1, title="Methods", text="x", section_type=SectionType.METHODOLOGY)
        )
        == "methodology"
    )
    assert (
        _detect_section_focus(
            SectionInfo(
                number=1,
                title="Discussion",
                text="x",
                section_type=SectionType.DISCUSSION,
            )
        )
        == "discussion"
    )
    assert (
        _detect_section_focus(
            SectionInfo(
                number=1,
                title="Proof",
                text="x" * 600,
                section_type=SectionType.OTHER,
                math_content=True,
            )
        )
        == "proof"
    )


def test_review_section_chains_verify_for_proof_sections():
    section_agent = Mock()
    verify_agent = Mock()
    first_pass = [_comment(1)]
    verified = [_comment(2)]
    section_agent.run.return_value = first_pass
    verify_agent.run.return_value = verified
    section = SectionInfo(
        number=1,
        title="Proof",
        text="x" * 600,
        section_type=SectionType.OTHER,
        math_content=True,
    )

    # A paper_markdown that contains the mock comments' quote verbatim so
    # the internal `_verify_with_fallback` calls in `_review_section` find
    # the quote and don't stamp an `[approximate]` prefix on it. The mock
    # `_comment()` returns a DetailedComment whose .quote is the literal
    # string below, so placing it inside paper_markdown is enough.
    paper_markdown = "Preface.\n\nThis is a sufficiently long quote from the paper.\n\nTrailer."

    result = _review_section(
        section_agent,
        verify_agent,
        section,
        paper_markdown,
        "Paper",
        _overview(),
        None,
        "proof",
        "",
        [section],
        "Abstract",
    )

    assert result == verified
    section_agent.run.assert_called_once()
    verify_agent.run.assert_called_once()


def test_review_section_handles_empty_comments_without_crashing():
    """Regression: a section agent that returns ``[]`` (no issues worth
    flagging) must propagate cleanly through ``_review_section`` without
    crashing the proof-verify chain or the downstream quote-verify
    fallback.

    This is the pipeline-integration counterpart to the Pydantic
    envelope test in ``tests/test_section.py::
    test_section_agent_accepts_empty_comments_list``, which only
    covers the agent's run() method with a MagicMock'd client. This
    test wires the section agent through ``_review_section`` (the
    exact call site used by the pipeline at pipeline.py::review_paper)
    and asserts that an empty result:

      1. Does NOT trigger the proof-verify chain (the ``if focus ==
         "proof" and comments and ...`` guard at review_stages.py:110
         must short-circuit on an empty list).
      2. Does NOT crash ``_verify_with_fallback``, which is called
         unconditionally after the section agent runs.
      3. Propagates as an empty list rather than None or a crash.

    Before the ``min_length=1`` constraint was dropped from
    ``_SectionComments.comments`` in src/coarse/agents/section.py,
    an empty result crashed with ``List should have at least 1
    item`` inside instructor's validation layer — never reaching
    _review_section at all. After the drop, it's the caller's
    responsibility to handle an empty list gracefully, and this
    test pins that responsibility.
    """
    section_agent = Mock()
    verify_agent = Mock()
    # Section agent legitimately finds no issues worth flagging.
    section_agent.run.return_value = []

    section = SectionInfo(
        number=1,
        title="Proof",
        text="x" * 600,
        section_type=SectionType.OTHER,
        math_content=True,  # Would normally trigger proof verify.
    )
    paper_markdown = "Preface.\n\nThis is a sufficiently long quote from the paper.\n\nTrailer."

    result = _review_section(
        section_agent,
        verify_agent,
        section,
        paper_markdown,
        "Paper",
        _overview(),
        None,
        "proof",  # Focus is proof, but empty list must still short-circuit.
        "",
        [section],
        "Abstract",
    )

    # Empty list propagates cleanly — not None, not a crash, not the
    # mock's return_value being mis-wrapped.
    assert result == []
    # Section agent was called exactly once (the main review pass).
    section_agent.run.assert_called_once()
    # Proof verify was NOT called — the `and comments and ...` guard at
    # review_stages.py:110 short-circuits when `comments` is falsy
    # (empty list). This is the regression the min_length=1 drop
    # exposes: without the short-circuit, verify_agent.run would be
    # called with [] and probably crash when it tries to iterate
    # comments internally.
    verify_agent.run.assert_not_called()


def test_run_editorial_pass_falls_back_to_crossref_and_critique():
    # `run_editorial_pass` finishes each agent pass with
    # `_verify_with_fallback`, which runs the real `verify_quotes` on the
    # paper markdown and stamps `[approximate]` on any quote it can't find.
    # The mock `_comment()` returns a DetailedComment whose `.quote` is
    # the literal string below, so the paper text must contain it to get
    # clean equality with the `crossref_comments` / `critique_comments`
    # lists this test asserts against.
    paper_text = "This is a sufficiently long quote from the paper."
    with (
        patch("coarse.review_stages.EditorialAgent") as MockEditorial,
        patch("coarse.review_stages.CrossrefAgent") as MockCrossref,
        patch("coarse.review_stages.CritiqueAgent") as MockCritique,
    ):
        MockEditorial.return_value.run.side_effect = RuntimeError("boom")
        crossref_comments = [_comment(10)]
        critique_comments = [_comment(11)]
        MockCrossref.return_value.run.return_value = crossref_comments
        MockCritique.return_value.run.return_value = critique_comments

        result = run_editorial_pass(
            Mock(),
            paper_text,
            _overview(),
            [_comment(1)],
            title="Paper",
            abstract="Abstract",
            author_notes="please focus on identification",
        )

    assert result == critique_comments
    MockCrossref.return_value.run.assert_called_once()
    MockCritique.return_value.run.assert_called_once()


def test_run_editorial_pass_returns_editorial_output_without_fallback():
    editorial_comments = [_comment(20)]

    class EditorialStub:
        def __init__(self, client):
            self.client = client

        def run(self, *args, **kwargs):
            return editorial_comments

    class CrossrefStub:
        def __init__(self, client):
            raise AssertionError("crossref fallback should not run")

    class CritiqueStub:
        def __init__(self, client):
            raise AssertionError("critique fallback should not run")

    # paper_text must contain the mock quote so `_verify_with_fallback`
    # leaves it untouched — see the note in
    # test_run_editorial_pass_falls_back_to_crossref_and_critique.
    result = run_editorial_pass(
        Mock(),
        "This is a sufficiently long quote from the paper.",
        _overview(),
        [_comment(1)],
        editorial_agent_cls=EditorialStub,
        crossref_agent_cls=CrossrefStub,
        critique_agent_cls=CritiqueStub,
    )

    assert result == editorial_comments


def test_run_editorial_pass_returns_crossref_comments_when_critique_fails():
    crossref_comments = [_comment(30)]

    class EditorialStub:
        def __init__(self, client):
            self.client = client

        def run(self, *args, **kwargs):
            raise RuntimeError("boom")

    class CrossrefStub:
        def __init__(self, client):
            self.client = client

        def run(self, *args, **kwargs):
            return crossref_comments

    class CritiqueStub:
        def __init__(self, client):
            self.client = client

        def run(self, *args, **kwargs):
            raise RuntimeError("boom")

    # paper_text must contain the mock quote — see note above.
    result = run_editorial_pass(
        Mock(),
        "This is a sufficiently long quote from the paper.",
        _overview(),
        [_comment(1)],
        editorial_agent_cls=EditorialStub,
        crossref_agent_cls=CrossrefStub,
        critique_agent_cls=CritiqueStub,
    )

    assert result == crossref_comments


def test_calibrate_domain_returns_none_on_client_failure():
    client = Mock()
    client.complete.side_effect = RuntimeError("boom")
    structure = Mock(
        title="Paper",
        domain="social_sciences/economics",
        abstract="Abstract",
        sections=[Mock(number=1, title="Intro")],
    )

    assert calibrate_domain(structure, client) is None


def test_extract_contribution_returns_none_on_client_failure():
    client = Mock()
    client.complete.side_effect = RuntimeError("boom")
    structure = Mock(
        title="Paper",
        abstract="Abstract",
        sections=[
            SectionInfo(
                number=1,
                title="Intro",
                text="Intro text",
                section_type=SectionType.INTRODUCTION,
            )
        ],
    )

    assert extract_contribution(structure, client) is None


# --- #200: soft cap on the final comment count ---


def test_cap_comments_truncates_over_long_list_to_max():
    comments = [_comment(i + 1) for i in range(40)]
    capped = _cap_comments(comments)
    assert len(capped) == _MAX_FINAL_COMMENTS
    # Truncation keeps the leading (severity-ordered) comments in order.
    assert [c.number for c in capped] == list(range(1, _MAX_FINAL_COMMENTS + 1))


def test_cap_comments_leaves_well_sized_list_untouched():
    comments = [_comment(i + 1) for i in range(5)]
    assert _cap_comments(comments) == comments


def test_run_editorial_pass_caps_overlong_editorial_output():
    """#200: the cap is actually wired into run_editorial_pass — an editorial
    pass that under-dedups and returns >25 comments is truncated to the leading
    _MAX_FINAL_COMMENTS, in order. Guards against a future refactor dropping the
    _cap_comments wrap on a return site."""
    n = _MAX_FINAL_COMMENTS + 9
    quotes = [f"This is a sufficiently long verbatim quote number {i} here." for i in range(n)]
    paper_text = " ".join(quotes)
    editorial_comments = [
        DetailedComment(number=i + 1, title=f"Comment {i + 1}", quote=quotes[i], feedback="fb")
        for i in range(n)
    ]

    class EditorialStub:
        def __init__(self, client):
            self.client = client

        def run(self, *args, **kwargs):
            return editorial_comments

    class _NoFallback:
        def __init__(self, client):
            raise AssertionError("fallback should not run when editorial succeeds")

    result = run_editorial_pass(
        Mock(),
        paper_text,
        _overview(),
        [_comment(1)],
        editorial_agent_cls=EditorialStub,
        crossref_agent_cls=_NoFallback,
        critique_agent_cls=_NoFallback,
    )

    assert len(result) == _MAX_FINAL_COMMENTS
    assert [c.number for c in result] == list(range(1, _MAX_FINAL_COMMENTS + 1))
