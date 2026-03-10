"""Tests for coarse.agents.literature — literature search agent."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from coarse.agents.literature import (
    ArxivPaper,
    _compile_context,
    _parse_arxiv_response,
    _RankedResult,
    _RankedResults,
    _search_perplexity,
    _SearchQueries,
    search_literature,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_ARXIV_XML = b"""\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.12345v1</id>
    <title>A Great Paper on Causal Inference</title>
    <summary>We propose a new method for causal inference using distributional approaches.</summary>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <published>2023-01-15T00:00:00Z</published>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2302.67890v2</id>
    <title>Instrumental Variables Revisited</title>
    <summary>A comprehensive review of IV methods in econometrics.</summary>
    <author><name>Carol White</name></author>
    <published>2023-02-20T00:00:00Z</published>
  </entry>
</feed>
"""


# ---------------------------------------------------------------------------
# Tests: XML parsing
# ---------------------------------------------------------------------------

def test_parse_arxiv_response_extracts_papers():
    papers = _parse_arxiv_response(SAMPLE_ARXIV_XML)
    assert len(papers) == 2
    assert papers[0].arxiv_id == "2301.12345v1"
    assert papers[0].title == "A Great Paper on Causal Inference"
    assert papers[0].authors == ["Alice Smith", "Bob Jones"]
    assert "distributional" in papers[0].abstract
    assert papers[0].published == "2023-01-15"


def test_parse_arxiv_response_second_paper():
    papers = _parse_arxiv_response(SAMPLE_ARXIV_XML)
    assert papers[1].arxiv_id == "2302.67890v2"
    assert papers[1].title == "Instrumental Variables Revisited"
    assert papers[1].authors == ["Carol White"]


def test_parse_empty_response():
    empty_xml = b'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    papers = _parse_arxiv_response(empty_xml)
    assert papers == []


# ---------------------------------------------------------------------------
# Tests: context compilation
# ---------------------------------------------------------------------------

def test_compile_context_formats_papers():
    papers = {
        "2301.12345": ArxivPaper(
            arxiv_id="2301.12345",
            title="Test Paper",
            authors=["Alice", "Bob", "Carol", "Dave"],
            abstract="Abstract text",
            published="2023-01-15",
        ),
    }
    ranked = [_RankedResult(arxiv_id="2301.12345", relevance_score=0.9, reason="Directly related")]
    result = _compile_context(ranked, papers)
    assert "Test Paper" in result
    assert "Alice, Bob, Carol et al." in result
    assert "arXiv:2301.12345" in result
    assert "Directly related" in result


def test_compile_context_empty():
    result = _compile_context([], {})
    assert result == ""


# ---------------------------------------------------------------------------
# Tests: search_literature integration (mocked HTTP + LLM) — arXiv fallback
# ---------------------------------------------------------------------------

def test_search_literature_arxiv_end_to_end():
    """Full arXiv pipeline with mocked arXiv API and LLM calls (no OPENROUTER_API_KEY)."""
    mock_client = MagicMock()

    # First LLM call: query generation
    # Second LLM call: ranking
    mock_client.complete.side_effect = [
        _SearchQueries(queries=["causal inference distributional"]),
        _RankedResults(
            ranked=[
                _RankedResult(arxiv_id="2301.12345v1", relevance_score=0.9, reason="Core method"),
                _RankedResult(
                    arxiv_id="2302.67890v2", relevance_score=0.7,
                    reason="Related review",
                ),
            ],
            refinement_queries=[],
        ),
    ]

    with (
        patch("coarse.agents.literature._search_arxiv") as mock_search,
        patch.dict("os.environ", {}, clear=False),
    ):
        # Ensure no OPENROUTER_API_KEY so we hit arXiv path
        env = dict(__builtins__=None)  # noqa: F841
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False):
            mock_search.return_value = [
                ArxivPaper(
                    arxiv_id="2301.12345v1", title="Causal Paper",
                    authors=["Alice"], abstract="Abstract", published="2023-01-15",
                ),
                ArxivPaper(
                    arxiv_id="2302.67890v2", title="IV Review",
                    authors=["Bob"], abstract="Abstract", published="2023-02-20",
                ),
            ]
            result = search_literature("My Paper", "My abstract", mock_client)

    assert "Causal Paper" in result
    assert "IV Review" in result
    assert mock_client.complete.call_count == 2


def test_search_literature_query_generation_fails():
    """If query generation fails, fallback to title-based search."""
    mock_client = MagicMock()
    mock_client.complete.side_effect = [
        Exception("LLM failed"),
        _RankedResults(
            ranked=[
                _RankedResult(arxiv_id="2301.12345v1", relevance_score=0.8, reason="Related"),
            ],
            refinement_queries=[],
        ),
    ]

    with (
        patch("coarse.agents.literature._search_arxiv") as mock_search,
        patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False),
    ):
        mock_search.return_value = [
            ArxivPaper(
                arxiv_id="2301.12345v1", title="Fallback Paper",
                authors=["Alice"], abstract="Abstract", published="2023-01-15",
            ),
        ]
        result = search_literature("My Title", "My abstract", mock_client)

    # Should still produce results using title as fallback query
    assert "Fallback Paper" in result


def test_search_literature_no_results():
    """If arXiv returns nothing, return empty string."""
    mock_client = MagicMock()
    mock_client.complete.return_value = _SearchQueries(queries=["nonexistent topic xyz"])

    with (
        patch("coarse.agents.literature._search_arxiv", return_value=[]),
        patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False),
    ):
        result = search_literature("Nonexistent", "Nothing", mock_client)

    assert result == ""


# ---------------------------------------------------------------------------
# Tests: Perplexity path
# ---------------------------------------------------------------------------

def test_search_perplexity_happy_path():
    """_search_perplexity returns content and tracks cost."""
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "## Related Work\n1. Paper A by Author (2020)"

    with patch("coarse.agents.literature.litellm") as mock_litellm:
        mock_litellm.completion.return_value = mock_response
        mock_litellm.completion_cost.return_value = 0.025

        result = _search_perplexity("Test Title", "Test abstract", mock_client)

    assert "Paper A" in result
    mock_client.add_cost.assert_called_once_with(0.025)


def test_search_perplexity_empty_response_raises():
    """_search_perplexity raises ValueError on empty response."""
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = ""

    with patch("coarse.agents.literature.litellm") as mock_litellm:
        mock_litellm.completion.return_value = mock_response

        try:
            _search_perplexity("Test", "Abstract", mock_client)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass


def test_dispatcher_uses_perplexity_when_key_set():
    """search_literature dispatches to Perplexity when OPENROUTER_API_KEY is set."""
    mock_client = MagicMock()

    with (
        patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test-key"}, clear=False),
        patch(
            "coarse.agents.literature._search_perplexity",
            return_value="Perplexity results",
        ) as mock_perp,
        patch("coarse.agents.literature._search_arxiv_pipeline") as mock_arxiv,
    ):
        result = search_literature("Title", "Abstract", mock_client)

    assert result == "Perplexity results"
    mock_perp.assert_called_once()
    mock_arxiv.assert_not_called()


def test_dispatcher_falls_back_on_perplexity_failure():
    """search_literature falls back to arXiv when Perplexity raises."""
    mock_client = MagicMock()

    with (
        patch.dict("os.environ", {"OPENROUTER_API_KEY": "sk-test-key"}, clear=False),
        patch("coarse.agents.literature._search_perplexity", side_effect=Exception("API error")),
        patch(
            "coarse.agents.literature._search_arxiv_pipeline",
            return_value="arXiv results",
        ) as mock_arxiv,
    ):
        result = search_literature("Title", "Abstract", mock_client)

    assert result == "arXiv results"
    mock_arxiv.assert_called_once()


def test_dispatcher_uses_arxiv_when_no_key():
    """search_literature uses arXiv when OPENROUTER_API_KEY is not set."""
    mock_client = MagicMock()

    with (
        patch.dict("os.environ", {"OPENROUTER_API_KEY": ""}, clear=False),
        patch("coarse.agents.literature._search_perplexity") as mock_perp,
        patch(
            "coarse.agents.literature._search_arxiv_pipeline",
            return_value="arXiv results",
        ) as mock_arxiv,
    ):
        result = search_literature("Title", "Abstract", mock_client)

    assert result == "arXiv results"
    mock_perp.assert_not_called()
    mock_arxiv.assert_called_once()
