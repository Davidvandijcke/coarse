"""Shared test fixtures for coarse."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    PaperText,
    SectionInfo,
    SectionType,
)

# Use this in tests where the model string is arbitrary (mocked LLM calls).
# Keep real model IDs only where tests validate provider-specific behavior.
TEST_MODEL = "test/mock-model"


@pytest.fixture(autouse=True)
def _isolate_ocr_retry_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep ``COARSE_OCR_MAX_RETRIES`` out of the test environment by default.

    ``src/coarse/extraction_openrouter.py::_get_ocr_max_retries`` honors
    the ``COARSE_OCR_MAX_RETRIES`` env var at call time. Several tests
    in ``tests/test_extraction.py`` import the module-level
    ``_OCR_MAX_RETRIES = 9`` constant and assert things like
    ``post_mock.call_count == 2 * (_OCR_MAX_RETRIES + 1)``. If a shell
    or CI job happens to set ``COARSE_OCR_MAX_RETRIES=2`` before
    ``pytest`` runs — or if a stray test forgets to clean up after
    itself — those call-count assertions silently break in ways that
    masquerade as a retry-loop regression.

    Make the default testing environment clean by unsetting the var
    before every test. Tests that explicitly want to exercise the
    override (``test_openrouter_ocr_honors_env_override_retries``,
    ``test_openrouter_ocr_invalid_env_override_falls_back_to_default``)
    set it through ``monkeypatch.setenv`` / ``patch.dict``, which
    supersedes this fixture for the duration of the test.
    """
    monkeypatch.delenv("COARSE_OCR_MAX_RETRIES", raising=False)


def make_comment(number: int = 1, **overrides) -> DetailedComment:
    """Factory for DetailedComment with sensible defaults."""
    defaults = {
        "number": number,
        "title": f"Comment {number}",
        "quote": "Some verbatim quote from the paper text.",
        "feedback": f"Feedback for comment {number}.",
    }
    defaults.update(overrides)
    return DetailedComment(**defaults)


def make_mock_client() -> MagicMock:
    """Factory for a mocked LLMClient."""
    from coarse.llm import LLMClient

    client = MagicMock(spec=LLMClient)
    client.supports_prompt_caching = False
    return client


@pytest.fixture
def sample_comment():
    """A minimal valid DetailedComment."""
    return DetailedComment(
        number=1,
        title="Test Comment",
        quote="Some verbatim quote from the paper text.",
        feedback="Some feedback.",
    )


@pytest.fixture
def sample_section():
    """A minimal valid SectionInfo."""
    return SectionInfo(
        number=1,
        title="Introduction",
        text="Content of section. " * 20,
        section_type=SectionType.INTRODUCTION,
    )


@pytest.fixture
def sample_overview():
    """A minimal valid OverviewFeedback with 4 issues."""
    return OverviewFeedback(
        issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}.") for i in range(1, 5)]
    )


@pytest.fixture
def sample_paper_text():
    """A minimal valid PaperText."""
    return PaperText(full_markdown="Full paper markdown.", token_estimate=500)


@pytest.fixture
def sample_structure():
    """A minimal valid PaperStructure."""
    return PaperStructure(
        title="Test Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="This is the abstract.",
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text="Introduction content. " * 20,
                section_type=SectionType.INTRODUCTION,
            )
        ],
    )
