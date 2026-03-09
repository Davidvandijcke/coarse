"""Shared test fixtures for coarse."""

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
