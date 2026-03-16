"""Tests for extraction quality gate (_check_extraction_quality)."""
from __future__ import annotations

from coarse.pipeline import _check_extraction_quality
from coarse.types import (
    PaperStructure,
    SectionInfo,
    SectionType,
)


def _make_structure(
    section_count: int = 2,
    text_length: int = 300,
) -> PaperStructure:
    sections = [
        SectionInfo(
            number=i + 1,
            title=f"Section {i + 1}",
            text="x" * text_length,
            section_type=SectionType.INTRODUCTION,
        )
        for i in range(section_count)
    ]
    return PaperStructure(
        title="Test",
        domain="test",
        taxonomy="test",
        abstract="Abstract",
        sections=sections,
    )


def test_good_extraction_passes():
    """Structure with sections and sufficient text passes."""
    structure = _make_structure()
    assert _check_extraction_quality(structure) is True


def test_no_sections_fails():
    """Structure with no sections fails."""
    structure = _make_structure(section_count=0)
    assert _check_extraction_quality(structure) is False


def test_insufficient_text_fails():
    """Structure with sections but very little text fails."""
    structure = _make_structure(section_count=2, text_length=10)
    assert _check_extraction_quality(structure) is False
