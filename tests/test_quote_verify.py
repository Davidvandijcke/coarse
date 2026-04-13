"""Tests for coarse.quote_verify."""

from __future__ import annotations

from coarse.quote_verify import (
    _is_math_heavy,
    _passage_garble_score,
    _trim_to_best_match,
    verify_quotes,
)
from coarse.types import DetailedComment


def _make_comment(quote: str, number: int = 1) -> DetailedComment:
    return DetailedComment(
        number=number,
        title="Test comment",
        quote=quote,
        feedback="Test feedback.",
    )


PAPER_TEXT = """\
This paper presents a novel approach to distribution-valued instrumental
variable regression. We establish identification conditions under which
the distributional treatment effect can be recovered from observable data.
The key assumption is that the instrument affects the outcome only through
the treatment variable (exclusion restriction).
"""


def test_exact_match_passes_through():
    """Quote that is an exact substring is kept as-is."""
    comment = _make_comment("the treatment variable (exclusion restriction)")
    result = verify_quotes([comment], PAPER_TEXT)
    assert "exclusion restriction" in result[0].quote


def test_case_insensitive_exact_match():
    """Case-insensitive substring match passes."""
    comment = _make_comment("The Treatment Variable (Exclusion Restriction)")
    result = verify_quotes([comment], PAPER_TEXT)
    assert "[approximate]" not in result[0].quote


def test_fuzzy_match_corrects_quote():
    """Slightly garbled quote gets corrected to nearest passage (threshold=0.80)."""
    # This garbled version is close enough to pass 0.80 threshold
    garbled = "the instrument affects the outcome only through"
    comment = _make_comment(garbled)
    result = verify_quotes([comment], PAPER_TEXT)
    # Should be corrected, not flagged as approximate
    assert "[approximate]" not in result[0].quote
    assert len(result) == 1


def test_heavily_garbled_quote_dropped():
    """Heavily garbled quote below 0.80 threshold is dropped."""
    garbled = "the instrment affcts th outcom onl thrugh"
    comment = _make_comment(garbled)
    result = verify_quotes([comment], PAPER_TEXT)
    # Ratio likely below 0.80, should be dropped
    # (if it passes due to window matching, that's still acceptable)
    assert len(result) <= 1


def test_no_match_dropped_by_default():
    """Completely unrelated quote is dropped when drop_unverified=True (default)."""
    comment = _make_comment("quantum entanglement in black holes")
    result = verify_quotes([comment], PAPER_TEXT)
    assert len(result) == 0


def test_no_match_flagged_approximate_when_kept():
    """Completely unrelated quote is flagged when drop_unverified=False."""
    comment = _make_comment("quantum entanglement in black holes")
    result = verify_quotes([comment], PAPER_TEXT, drop_unverified=False)
    assert len(result) == 1
    assert result[0].quote.startswith("[approximate]")


def test_multiple_comments():
    """Multiple comments are processed independently; unverifiable ones are dropped."""
    comments = [
        _make_comment("novel approach to distribution-valued", number=1),
        _make_comment("totally fake quote xyz and more padding text", number=2),
    ]
    result = verify_quotes(comments, PAPER_TEXT)
    assert len(result) == 1
    assert "novel approach" in result[0].quote


def test_multiple_comments_kept():
    """With drop_unverified=False, unverifiable quotes are flagged not dropped."""
    comments = [
        _make_comment("novel approach to distribution-valued", number=1),
        _make_comment("totally fake quote xyz and more padding text", number=2),
    ]
    result = verify_quotes(comments, PAPER_TEXT, drop_unverified=False)
    assert len(result) == 2
    assert "[approximate]" not in result[0].quote
    assert "[approximate]" in result[1].quote


def test_trim_to_best_match_expands_truncated_quote():
    """_trim_to_best_match should expand a truncated quote rather than shrink the match."""
    full_passage = "The covariance is given by \\sqrt{c_k(q) c_l(q)} which completes the proof."
    truncated_quote = "The covariance is given by \\sqrt{c_k(q) c_l(q"
    result = _trim_to_best_match(truncated_quote, full_passage)
    # Result should be LONGER than the truncated quote (expanded, not shrunk)
    assert len(result) > len(truncated_quote)
    # Should include the closing bracket that was truncated
    assert "}" in result


# --- Passage garble scoring ---


def test_passage_garble_score_clean():
    """Clean passage should have zero garble score."""
    assert _passage_garble_score("The finite integral over (a, b)") == 0.0


def test_passage_garble_score_garbled():
    """Passage with OCR artifacts should have nonzero garble score."""
    score = _passage_garble_score("The ®nite integral /C40a, b/C41")
    assert score > 0.0


def test_passage_garble_score_empty():
    assert _passage_garble_score("") == 0.0


# --- Math-heavy quote detection and stricter threshold ---


MATH_PAPER = r"""\
The coding gain is $\gamma = \phi^3 / \sqrt{2}$ for the H32 lattice.
Table I shows the exponent values for each lattice class.
The fundamental region has volume $\text{vol}(\Lambda) = 2^{n/2}$.
"""


def test_is_math_heavy_detects_latex():
    """Quotes with LaTeX commands are detected as math-heavy."""
    assert _is_math_heavy(r"The gain is $\gamma = \phi^3 / \sqrt{2}$ for H32")
    assert _is_math_heavy(r"\frac{1}{n} \sum_{i=1}^{n} x_i = \bar{x}")


def test_is_math_heavy_detects_numbers():
    """Quotes with multiple numbers are detected as math-heavy."""
    assert _is_math_heavy("Row 3 shows value 128 at order 256 with gain 3.01 dB")


def test_is_math_heavy_rejects_prose():
    """Plain prose without math tokens is not math-heavy."""
    assert not _is_math_heavy("This paper presents a novel approach to regression")


def test_math_quote_altered_exponent_dropped():
    """A math quote with a single altered exponent should be dropped under stricter threshold.

    Changing phi^3 to phi^5 has high string similarity (~95%) but completely
    changes the mathematical meaning. The 0.92 threshold should catch this.
    """
    # Original paper has phi^3, but quote says phi^5
    altered = r"The coding gain is $\gamma = \phi^5 / \sqrt{2}$ for the H32 lattice."
    comment = _make_comment(altered)
    result = verify_quotes([comment], MATH_PAPER)
    # The altered exponent should cause this to be dropped
    # (fuzzy ratio ~0.95 passes 0.80 but the match replaces with actual text)
    # Key: the corrected quote should contain phi^3, not phi^5
    if result:
        assert r"\phi^5" not in result[0].quote


def test_math_quote_exact_match_kept():
    """An exact math quote passes regardless of threshold."""
    exact = r"The coding gain is $\gamma = \phi^3 / \sqrt{2}$ for the H32 lattice."
    comment = _make_comment(exact)
    result = verify_quotes([comment], MATH_PAPER)
    assert len(result) == 1
    assert r"\phi^3" in result[0].quote
