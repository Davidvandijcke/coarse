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


def test_tokenize_text_extracts_word_tokens():
    tokens = tokenize_text("Hello, world! Equation x_1 = 2.")

    assert "hello" in tokens
    assert "world" in tokens
    assert "x_1" in tokens


def test_jaccard_similarity_handles_overlap():
    assert jaccard_similarity({"a", "b", "c"}, {"b", "c", "d"}) == 0.5
