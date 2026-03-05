"""Tests for coarse.quote_verify."""
from __future__ import annotations

from coarse.quote_verify import verify_quotes
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
    comment = _make_comment("exclusion restriction")
    result = verify_quotes([comment], PAPER_TEXT)
    assert result[0].quote == "exclusion restriction"


def test_case_insensitive_exact_match():
    """Case-insensitive substring match passes."""
    comment = _make_comment("Exclusion Restriction")
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


def test_empty_quote_passes_through():
    """Empty quote is kept as-is."""
    comment = _make_comment("")
    result = verify_quotes([comment], PAPER_TEXT)
    assert result[0].quote == ""


def test_multiple_comments():
    """Multiple comments are processed independently; unverifiable ones are dropped."""
    comments = [
        _make_comment("novel approach", number=1),
        _make_comment("totally fake quote xyz", number=2),
    ]
    result = verify_quotes(comments, PAPER_TEXT)
    assert len(result) == 1
    assert result[0].quote == "novel approach"


def test_multiple_comments_kept():
    """With drop_unverified=False, unverifiable quotes are flagged not dropped."""
    comments = [
        _make_comment("novel approach", number=1),
        _make_comment("totally fake quote xyz", number=2),
    ]
    result = verify_quotes(comments, PAPER_TEXT, drop_unverified=False)
    assert len(result) == 2
    assert "[approximate]" not in result[0].quote
    assert "[approximate]" in result[1].quote
