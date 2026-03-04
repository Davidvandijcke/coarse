"""Tests for section routing (detect_section_focus)."""
from __future__ import annotations

from coarse.pipeline import detect_section_focus
from coarse.types import SectionInfo, SectionType


def _make_section(text: str, section_type: SectionType = SectionType.OTHER) -> SectionInfo:
    return SectionInfo(
        number=1, title="Test", text=text, section_type=section_type,
    )


def test_proof_keyword_theorem():
    section = _make_section("We now state the main theorem and provide its proof.")
    assert detect_section_focus(section) == "proof"


def test_proof_keyword_lemma():
    section = _make_section("Lemma 3.2 establishes the upper bound.")
    assert detect_section_focus(section) == "proof"


def test_proof_keyword_qed():
    section = _make_section("This completes the argument. QED")
    assert detect_section_focus(section) == "proof"


def test_methodology_type():
    section = _make_section("We use OLS regression.", SectionType.METHODOLOGY)
    assert detect_section_focus(section) == "methodology"


def test_literature_type():
    section = _make_section("Prior work has explored...", SectionType.RELATED_WORK)
    assert detect_section_focus(section) == "literature"


def test_general_fallback():
    section = _make_section("This section presents results.", SectionType.RESULTS)
    assert detect_section_focus(section) == "general"


def test_proof_keyword_overrides_type():
    """Proof keywords take priority over section_type."""
    section = _make_section(
        "We prove the following proposition.", SectionType.RESULTS,
    )
    assert detect_section_focus(section) == "proof"
