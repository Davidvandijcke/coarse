"""Tests for domain calibration (types and prompt formatting)."""
from __future__ import annotations

from coarse.prompts import _format_calibration, calibration_user, overview_user, section_user
from coarse.types import DomainCalibration, SectionInfo, SectionType


def _make_calibration() -> DomainCalibration:
    return DomainCalibration(
        methodology_concerns=["Proof completeness", "Regularity conditions"],
        assumption_red_flags=["Smoothness on discrete data"],
        what_not_to_check=["Empirical validation"],
        evaluation_standards=["Complete proofs required"],
    )


def test_domain_calibration_model():
    """DomainCalibration can be constructed and serialized."""
    cal = _make_calibration()
    assert len(cal.methodology_concerns) == 2
    assert "Empirical validation" in cal.what_not_to_check


def test_format_calibration():
    """_format_calibration produces readable text block."""
    cal = _make_calibration()
    text = _format_calibration(cal)
    assert "Proof completeness" in text
    assert "Empirical validation" in text
    assert "Domain-Specific Review Calibration" in text


def test_overview_user_with_calibration():
    """overview_user includes calibration when provided."""
    cal = _make_calibration()
    result = overview_user("Title", "Abstract", "Sections", calibration=cal)
    assert "Proof completeness" in result
    assert "Empirical validation" in result


def test_overview_user_without_calibration():
    """overview_user works without calibration (backward compat)."""
    result = overview_user("Title", "Abstract", "Sections")
    assert "Domain-Specific" not in result


def test_section_user_with_calibration():
    """section_user includes calibration when provided."""
    cal = _make_calibration()
    section = SectionInfo(
        number=1, title="Methods", text="Some text.",
        section_type=SectionType.METHODOLOGY,
    )
    result = section_user("Paper", section, calibration=cal)
    assert "Proof completeness" in result


def test_calibration_user_prompt():
    """calibration_user produces a well-formed prompt."""
    result = calibration_user("Title", "math/algebra", "Abstract", "1. Intro, 2. Proofs")
    assert "Title" in result
    assert "math/algebra" in result
