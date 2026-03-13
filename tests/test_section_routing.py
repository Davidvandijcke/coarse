"""Tests for section routing (detect_section_focus)."""
from __future__ import annotations

from coarse.pipeline import detect_section_focus
from coarse.types import SectionInfo, SectionType


def _make_section(
    text: str = "Some section text.",
    section_type: SectionType = SectionType.OTHER,
    math_content: bool = False,
) -> SectionInfo:
    return SectionInfo(
        number=1, title="Test", text=text, section_type=section_type,
        math_content=math_content,
    )


def test_math_content_returns_proof():
    section = _make_section(math_content=True)
    assert detect_section_focus(section) == "proof"


def test_math_content_overrides_type():
    """math_content takes priority over section_type."""
    section = _make_section(section_type=SectionType.RESULTS, math_content=True)
    assert detect_section_focus(section) == "proof"


def test_methodology_type():
    section = _make_section("We use OLS regression.", SectionType.METHODOLOGY)
    assert detect_section_focus(section) == "methodology"


def test_literature_type():
    section = _make_section("Prior work has explored...", SectionType.RELATED_WORK)
    assert detect_section_focus(section) == "literature"


def test_results_type():
    section = _make_section("This section presents results.", SectionType.RESULTS)
    assert detect_section_focus(section) == "results"


def test_general_fallback():
    section = _make_section("This section discusses implications.", SectionType.DISCUSSION)
    assert detect_section_focus(section) == "general"
