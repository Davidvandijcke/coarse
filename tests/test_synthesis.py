"""Tests for coarse.synthesis.render_review."""

from __future__ import annotations

from coarse.synthesis import render_review
from coarse.types import (
    DetailedComment,
    LanguageContext,
    OverviewFeedback,
    OverviewIssue,
    Review,
)


def _make_review(
    *,
    title: str = "Test Paper",
    domain: str = "social_sciences/economics",
    taxonomy: str = "academic/research_paper",
    date: str = "3/3/2026, 11:23:50 AM",
    issues: list[OverviewIssue] | None = None,
    comments: list[DetailedComment] | None = None,
) -> Review:
    if issues is None:
        issues = [OverviewIssue(title=f"Issue {i}", body=f"Body {i}") for i in range(1, 5)]
    if comments is None:
        comments = [
            DetailedComment(
                number=1,
                title="Comment One",
                quote="Some quoted text from the paper for testing purposes.",
                feedback="Some feedback.",
            )
        ]
    return Review(
        title=title,
        domain=domain,
        taxonomy=taxonomy,
        date=date,
        overall_feedback=OverviewFeedback(issues=issues),
        detailed_comments=comments,
    )


def test_render_review_returns_string():
    review = _make_review()
    result = render_review(review)
    assert isinstance(result, str)
    assert len(result) > 0


def test_render_review_header():
    review = _make_review(
        title="My Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="3/3/2026, 11:23:50 AM",
    )
    result = render_review(review)
    assert "# My Paper" in result
    assert "**Date**: 3/3/2026, 11:23:50 AM" in result
    assert "**Domain**: social_sciences/economics" in result
    assert "**Taxonomy**: academic/research_paper" in result
    assert "**Filter**: Active comments" in result


def test_render_review_overall_feedback():
    issues = [
        OverviewIssue(title="Alpha Issue", body="Alpha body text."),
        OverviewIssue(title="Beta Issue", body="Beta body text."),
        OverviewIssue(title="Gamma Issue", body="Gamma body text."),
        OverviewIssue(title="Delta Issue", body="Delta body text."),
    ]
    review = _make_review(issues=issues)
    result = render_review(review)

    assert "## Overall Feedback" in result
    assert "Here are some overall reactions to the document." in result
    for issue in issues:
        assert f"**{issue.title}**" in result
        assert issue.body in result

    # Single trailing [Pending] after the block, not after each issue
    assert result.count("**Status**: [Pending]") == len(review.detailed_comments) + 1
    # The overall status comes before the detailed comments section
    overall_idx = result.index("## Overall Feedback")
    detailed_idx = result.index("## Detailed Comments")
    first_pending = result.index("**Status**: [Pending]")
    assert overall_idx < first_pending < detailed_idx


def test_render_review_detailed_comments_count():
    comments = [
        DetailedComment(
            number=i,
            title=f"C{i}",
            quote=f"Verbatim quote text from section {i} of the paper.",
            feedback=f"f{i}",
        )
        for i in range(1, 6)
    ]
    review = _make_review(comments=comments)
    result = render_review(review)
    assert "## Detailed Comments (5)" in result


def test_render_review_no_severity_labels():
    """Severity labels like [CRITICAL] or [MINOR] must not appear in output."""
    comments = [
        DetailedComment(
            number=1,
            title="A critical issue",
            quote="Verbatim quote text from section one of the paper.",
            feedback="f1",
            severity="critical",
        ),
        DetailedComment(
            number=2,
            title="A minor issue",
            quote="Verbatim quote text from section two of the paper.",
            feedback="f2",
            severity="minor",
        ),
        DetailedComment(
            number=3,
            title="A major issue",
            quote="Verbatim quote text from section three of the paper.",
            feedback="f3",
            severity="major",
        ),
    ]
    review = _make_review(comments=comments)
    result = render_review(review)

    assert "[CRITICAL]" not in result
    assert "[MINOR]" not in result
    assert "[MAJOR]" not in result


def test_render_review_pipeline_order_preserved():
    """Comments should appear in pipeline order, not sorted by severity."""
    comments = [
        DetailedComment(
            number=1,
            title="Minor First",
            quote="Verbatim quote from section one.",
            feedback="f1",
            severity="minor",
        ),
        DetailedComment(
            number=2,
            title="Critical Second",
            quote="Verbatim quote from section two.",
            feedback="f2",
            severity="critical",
        ),
        DetailedComment(
            number=3,
            title="Major Third",
            quote="Verbatim quote from section three.",
            feedback="f3",
            severity="major",
        ),
    ]
    review = _make_review(comments=comments)
    result = render_review(review)

    # Comments should be in original order: 1, 2, 3
    idx_minor = result.index("### 1. Minor First")
    idx_critical = result.index("### 2. Critical Second")
    idx_major = result.index("### 3. Major Third")
    assert idx_minor < idx_critical < idx_major


def test_render_review_summary():
    """If overview has a summary, it should appear as **Outline** in output."""
    issues = [OverviewIssue(title=f"I{i}", body=f"b{i}") for i in range(1, 5)]
    overview = OverviewFeedback(
        summary="This paper studies X using method Y and finds Z.",
        issues=issues,
    )
    review = _make_review(issues=issues)
    # Manually set summary
    review = Review(
        title=review.title,
        domain=review.domain,
        taxonomy=review.taxonomy,
        date=review.date,
        overall_feedback=overview,
        detailed_comments=review.detailed_comments,
    )
    result = render_review(review)
    assert "**Outline**" in result
    assert "This paper studies X using method Y and finds Z." in result


def test_render_review_no_summary_when_empty():
    """If summary is empty, **Outline** should not appear."""
    review = _make_review()
    result = render_review(review)
    assert "**Outline**" not in result


def test_render_review_detailed_comment_fields():
    comment = DetailedComment(
        number=3,
        title="Missing Robustness",
        quote="The model assumes linearity.",
        feedback="Please add robustness checks.",
    )
    review = _make_review(comments=[comment])
    result = render_review(review)

    assert "### 3. Missing Robustness" in result
    assert "**Status**: [Pending]" in result
    assert "**Quote**:" in result
    assert "> The model assumes linearity." in result
    assert "**Feedback**:" in result
    assert "Please add robustness checks." in result

    # Verify order: status → quote → feedback
    status_idx = result.index("**Status**: [Pending]", result.index("### 3."))
    quote_idx = result.index("**Quote**:")
    feedback_idx = result.index("**Feedback**:")
    assert status_idx < quote_idx < feedback_idx


def test_render_review_multiline_quote():
    comment = DetailedComment(
        number=1,
        title="Multi-line",
        quote="First line.\nSecond line.\nThird line.",
        feedback="Fix it.",
    )
    review = _make_review(comments=[comment])
    result = render_review(review)

    assert "> First line." in result
    assert "> Second line." in result
    assert "> Third line." in result


def test_render_review_separator_count():
    comments = [
        DetailedComment(
            number=i,
            title=f"C{i}",
            quote=f"Verbatim quote text from section {i} of the paper.",
            feedback=f"f{i}",
        )
        for i in range(1, 4)
    ]
    review = _make_review(comments=comments)
    result = render_review(review)

    # Separators: after header block, after overall feedback, after each comment (3)
    separator_count = result.count("\n---\n")
    assert separator_count >= 5  # 2 structural + 3 per comment


def test_render_review_empty_comments():
    issues = [OverviewIssue(title=f"I{i}", body=f"b{i}") for i in range(1, 5)]
    review = _make_review(issues=issues, comments=[])
    result = render_review(review)

    assert "## Detailed Comments (0)" in result
    assert isinstance(result, str)
    assert len(result) > 0


# --- Recommendation rendering ---


def test_render_review_recommendation_present():
    """When recommendation is non-empty, it renders as **Recommendation**: ..."""
    issues = [OverviewIssue(title=f"I{i}", body=f"b{i}") for i in range(1, 5)]
    overview = OverviewFeedback(
        issues=issues,
        recommendation="Major revision. The core identification strategy needs strengthening.",
    )
    review = Review(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="3/3/2026, 11:23:50 AM",
        overall_feedback=overview,
        detailed_comments=[
            DetailedComment(
                number=1,
                title="C1",
                quote="Verbatim quote text from section one of the paper.",
                feedback="f1",
            )
        ],
    )
    result = render_review(review)
    assert "**Recommendation**: Major revision." in result
    # Recommendation should appear before the overall Status line
    rec_idx = result.index("**Recommendation**")
    status_idx = result.index("**Status**: [Pending]")
    assert rec_idx < status_idx


def test_render_review_recommendation_empty():
    """When recommendation is empty string, **Recommendation** should not appear."""
    review = _make_review()
    result = render_review(review)
    assert "**Recommendation**" not in result


# --- Revision targets rendering ---


def test_render_review_revision_targets_present():
    """When revision_targets is non-empty, they render as numbered list."""
    issues = [OverviewIssue(title=f"I{i}", body=f"b{i}") for i in range(1, 5)]
    overview = OverviewFeedback(
        issues=issues,
        recommendation="Major revision.",
        revision_targets=[
            "Strengthen identification strategy with formal sensitivity analysis.",
            "Add simulation study demonstrating finite-sample performance.",
            "Clarify the connection between Theorem 2 and the policy implications.",
        ],
    )
    review = Review(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="3/3/2026, 11:23:50 AM",
        overall_feedback=overview,
        detailed_comments=[
            DetailedComment(
                number=1,
                title="C1",
                quote="Verbatim quote text from section one of the paper.",
                feedback="f1",
            )
        ],
    )
    result = render_review(review)
    assert "**Key revision targets**:" in result
    assert "1. Strengthen identification strategy" in result
    assert "2. Add simulation study" in result
    assert "3. Clarify the connection" in result
    # Revision targets should appear before the overall Status line
    targets_idx = result.index("**Key revision targets**:")
    status_idx = result.index("**Status**: [Pending]")
    assert targets_idx < status_idx


def test_render_review_revision_targets_empty():
    """When revision_targets is empty list, **Key revision targets** should not appear."""
    review = _make_review()
    result = render_review(review)
    assert "**Key revision targets**" not in result


# --- Label localization ---
#
# render_review localizes the fixed structural labels (Date, Overall Feedback,
# Quote, ...) based on Review.language.review_language. English (None / "" /
# "en") must stay byte-identical to the pre-localization output; a non-English
# review_language swaps the labels (but never the user content).


def test_render_review_english_byte_identical_none_vs_en():
    """The English path is byte-identical whether Review.language is None
    (English default) or a populated LanguageContext whose review_language is
    "en". This is the invariant that keeps existing English output stable."""
    baseline = _make_review()
    assert baseline.language is None
    baseline_md = render_review(baseline)

    en = _make_review()
    en.language = LanguageContext(
        site_language="en",
        review_language="en",
        paper_language="en",
        text_direction="ltr",
        paper_language_source="detected",
    )
    en_md = render_review(en)

    assert en_md == baseline_md


def test_render_review_english_golden_labels():
    """Golden check on the exact English label lines so a future label change
    (or a regression in the catalog) is caught. These literals are the
    pre-localization English strings."""
    review = _make_review(
        title="Golden Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="3/3/2026, 11:23:50 AM",
        comments=[
            DetailedComment(
                number=1,
                title="Comment One",
                quote="A verbatim quote from the paper.",
                feedback="Some feedback.",
            )
        ],
    )
    result = render_review(review)

    assert "# Golden Paper" in result
    assert "**Date**: 3/3/2026, 11:23:50 AM" in result
    assert "**Domain**: social_sciences/economics" in result
    assert "**Taxonomy**: academic/research_paper" in result
    assert "**Filter**: Active comments" in result
    assert "## Overall Feedback" in result
    assert "Here are some overall reactions to the document." in result
    assert "**Status**: [Pending]" in result
    assert "## Detailed Comments (1)" in result
    assert "**Quote**:" in result
    assert "**Feedback**:" in result


def test_render_review_localized_spanish_labels():
    """A Spanish review_language swaps every fixed label to its Spanish form;
    the English labels must not appear anywhere in the output."""
    issues = [OverviewIssue(title=f"I{i}", body=f"b{i}") for i in range(1, 5)]
    overview = OverviewFeedback(
        summary="This paper studies X.",
        issues=issues,
        recommendation="Major revision.",
        revision_targets=["Strengthen the identification strategy."],
    )
    review = Review(
        title="Documento de prueba",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="3/3/2026, 11:23:50 AM",
        overall_feedback=overview,
        detailed_comments=[
            DetailedComment(
                number=1,
                title="Comentario uno",
                quote="Una cita textual del documento.",
                feedback="Algún comentario.",
            )
        ],
    )
    review.language = LanguageContext(
        site_language="es",
        review_language="es",
        paper_language="es",
        text_direction="ltr",
        paper_language_source="detected",
    )
    result = render_review(review)

    # Localized labels present.
    assert "**Fecha**:" in result
    assert "**Dominio**:" in result
    assert "**Taxonomía**:" in result
    assert "**Filtro**: Comentarios activos" in result
    assert "## Valoración general" in result
    assert "Estas son algunas reacciones generales al documento." in result
    assert "**Resumen**" in result
    assert "**Recomendación**: Major revision." in result
    assert "**Objetivos clave de revisión**:" in result
    assert "**Estado**: [Pendiente]" in result
    assert "## Comentarios detallados (1)" in result
    assert "**Cita**:" in result
    assert "**Comentarios**:" in result

    # English labels must NOT appear.
    assert "**Date**:" not in result
    assert "**Domain**:" not in result
    assert "**Taxonomy**:" not in result
    assert "**Filter**: Active comments" not in result
    assert "## Overall Feedback" not in result
    assert "Here are some overall reactions to the document." not in result
    assert "**Outline**" not in result
    assert "**Recommendation**:" not in result
    assert "**Key revision targets**:" not in result
    assert "**Status**: [Pending]" not in result
    assert "## Detailed Comments" not in result
    assert "**Quote**:" not in result
    assert "**Feedback**:" not in result

    # User content is untouched by localization.
    assert "# Documento de prueba" in result
    assert "Una cita textual del documento." in result
    assert "Algún comentario." in result
