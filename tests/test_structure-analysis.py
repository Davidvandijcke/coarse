from unittest.mock import MagicMock, patch

import pytest

from coarse.prompts import STRUCTURE_SYSTEM, structure_user
from coarse.structure import analyze_structure
from coarse.types import PageContent, PaperStructure, PaperText, SectionInfo, SectionType


def make_paper_text(markdown: str = "# My Paper\n\nAbstract here.\n\n## Intro\n\nText.") -> PaperText:
    return PaperText(
        full_markdown=markdown,
        pages=[PageContent(page_num=1, text=markdown)],
        token_estimate=50,
    )


def make_paper_structure() -> PaperStructure:
    return PaperStructure(
        title="My Paper",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="Abstract here.",
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text="Text.",
                section_type=SectionType.INTRODUCTION,
                claims=["Claim A"],
                definitions=[],
            )
        ],
    )


@pytest.fixture()
def mock_client():
    client = MagicMock()
    client.complete.return_value = make_paper_structure()
    return client


def test_analyze_structure_returns_paper_structure(mock_client):
    paper_text = make_paper_text()
    result = analyze_structure(paper_text, mock_client)
    assert isinstance(result, PaperStructure)
    assert result.title == "My Paper"
    assert result.domain == "social_sciences/economics"
    assert len(result.sections) == 1


def test_analyze_structure_passes_correct_messages(mock_client):
    markdown = "# Test\n\nSome content."
    paper_text = make_paper_text(markdown)
    analyze_structure(paper_text, mock_client)

    call_args = mock_client.complete.call_args
    messages = call_args[0][0]

    system_msg = next(m for m in messages if m["role"] == "system")
    user_msg = next(m for m in messages if m["role"] == "user")

    assert system_msg["content"] == STRUCTURE_SYSTEM
    assert markdown in user_msg["content"]


def test_analyze_structure_uses_low_temperature(mock_client):
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)

    call_kwargs = mock_client.complete.call_args[1]
    assert call_kwargs["temperature"] <= 0.2


def test_analyze_structure_uses_high_max_tokens(mock_client):
    paper_text = make_paper_text()
    analyze_structure(paper_text, mock_client)

    call_kwargs = mock_client.complete.call_args[1]
    assert call_kwargs["max_tokens"] >= 4096


def test_analyze_structure_propagates_llm_error(mock_client):
    mock_client.complete.side_effect = RuntimeError("LLM unavailable")
    paper_text = make_paper_text()

    with pytest.raises(RuntimeError, match="LLM unavailable"):
        analyze_structure(paper_text, mock_client)
