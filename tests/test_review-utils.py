"""Tests for review_utils.py."""

from coarse.review_utils import build_sections_text, jaccard_similarity, tokenize_text
from coarse.types import SectionInfo, SectionType


def test_build_sections_text_marks_empty_sections():
    sections = [
        SectionInfo(number=1, title="Intro", text="", section_type=SectionType.INTRODUCTION),
    ]

    result = build_sections_text(sections)

    assert "## 1. Intro" in result
    assert "(empty)" in result


def test_build_sections_text_formats_populated_sections_with_type_and_spacing():
    sections = [
        SectionInfo(
            number=1,
            title="Intro",
            text="First section text.",
            section_type=SectionType.INTRODUCTION,
        ),
        SectionInfo(
            number=2,
            title="Methods",
            text="Second section text.",
            section_type=SectionType.METHODOLOGY,
        ),
    ]

    result = build_sections_text(sections)

    assert "## 1. Intro (introduction)\nFirst section text." in result
    assert "\n\n## 2. Methods (methodology)\nSecond section text." in result


def test_tokenize_text_extracts_word_tokens():
    tokens = tokenize_text("Hello, world! Equation x_1 = 2.")

    assert "hello" in tokens
    assert "world" in tokens
    assert "x_1" in tokens


def test_tokenize_text_whitespace_mode_preserves_punctuation_sensitive_tokens():
    tokens = tokenize_text("p<0.05 alpha-beta", mode="whitespace")

    assert "p<0.05" in tokens
    assert "alpha-beta" in tokens


def test_jaccard_similarity_handles_overlap():
    assert jaccard_similarity({"a", "b", "c"}, {"b", "c", "d"}) == 0.5
