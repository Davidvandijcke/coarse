"""Literature search agent — finds related papers to ground the review.

Primary path: Perplexity Sonar Pro Search via OpenRouter (web-grounded, ~12s, ~$0.03).
Fallback path: arXiv API + 2 LLM calls (free API, slower, arXiv-only coverage).
"""

from __future__ import annotations

import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from pydantic import BaseModel, Field

from coarse.config import has_provider_key
from coarse.llm import LLMClient
from coarse.models import LITERATURE_SEARCH_MODEL
from coarse.prompts import (
    ARXIV_QUERY_GEN_SYSTEM,
    ARXIV_RANKING_SYSTEM,
    PERPLEXITY_SYSTEM,
    perplexity_user,
)

logger = logging.getLogger(__name__)

_ARXIV_API = "https://export.arxiv.org/api/query"
_MAX_RESULTS_PER_QUERY = 10
_MAX_ITERATIONS = 2
_TOP_K = 8
_PERPLEXITY_TEMPERATURE = 0.3
_QUERY_GEN_TEMPERATURE = 0.5
_RANKING_TEMPERATURE = 0.2

# Atom namespace used by arXiv API
_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass
class ArxivPaper:
    """Minimal representation of an arXiv search result."""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    published: str


# ---------------------------------------------------------------------------
# LLM response models
# ---------------------------------------------------------------------------


class _SearchQueries(BaseModel):
    """LLM-generated search queries for arXiv."""

    queries: list[str] = Field(min_length=1, max_length=5)


class _RankedResult(BaseModel):
    """A single ranked search result."""

    arxiv_id: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    reason: str


class _RankedResults(BaseModel):
    """LLM-ranked search results with optional refinement queries."""

    ranked: list[_RankedResult]
    refinement_queries: list[str] = Field(default_factory=list, max_length=3)


# ---------------------------------------------------------------------------
# Perplexity Sonar Pro Search (primary path)
# ---------------------------------------------------------------------------


def _search_perplexity(title: str, abstract: str, client: LLMClient) -> str:
    """Single Perplexity Sonar Pro Search call via LLMClient.complete_text.

    Returns formatted literature context string, or raises on failure. Routes
    through LLMClient so OpenRouter privacy / api_key / control-char stripping
    all apply uniformly with the rest of the pipeline.
    """
    perplexity_client = LLMClient(model=LITERATURE_SEARCH_MODEL)
    messages = [
        {"role": "system", "content": PERPLEXITY_SYSTEM},
        {"role": "user", "content": perplexity_user(title, abstract[:1500])},
    ]
    content = perplexity_client.complete_text(
        messages,
        max_tokens=4096,
        temperature=_PERPLEXITY_TEMPERATURE,
        timeout=60,
    )
    client.add_cost(perplexity_client.cost_usd)
    return content


# ---------------------------------------------------------------------------
# arXiv API helpers (stdlib only) — fallback path
# ---------------------------------------------------------------------------


def _search_arxiv(query: str, max_results: int = _MAX_RESULTS_PER_QUERY) -> list[ArxivPaper]:
    """Search arXiv API and parse Atom XML response."""
    params = urllib.parse.urlencode(
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
    )
    url = f"{_ARXIV_API}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml_data = resp.read()
    except Exception:
        logger.warning("arXiv API request failed for query: %s", query)
        return []

    return _parse_arxiv_response(xml_data)


def _parse_arxiv_response(xml_data: bytes) -> list[ArxivPaper]:
    """Parse arXiv Atom XML into ArxivPaper objects."""
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall("atom:entry", _NS):
        # Extract arxiv ID from the <id> URL
        id_url = entry.findtext("atom:id", default="", namespaces=_NS)
        arxiv_id = id_url.rsplit("/abs/", 1)[-1] if "/abs/" in id_url else id_url

        title = entry.findtext("atom:title", default="", namespaces=_NS).strip()
        title = " ".join(title.split())  # normalize whitespace

        abstract = entry.findtext("atom:summary", default="", namespaces=_NS).strip()
        abstract = " ".join(abstract.split())

        authors = [
            name.text.strip() for name in entry.findall("atom:author/atom:name", _NS) if name.text
        ]

        published = entry.findtext("atom:published", default="", namespaces=_NS)[:10]

        if title:
            papers.append(
                ArxivPaper(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract[:500],
                    published=published,
                )
            )

    return papers


# ---------------------------------------------------------------------------
# arXiv fallback pipeline
# ---------------------------------------------------------------------------


def _search_arxiv_pipeline(
    title: str,
    abstract: str,
    client: LLMClient,
) -> str:
    """Run the arXiv-based literature search (fallback path).

    Returns a formatted context block of related papers, or "" if search fails.
    """
    # Step 1: Generate search queries
    queries = _generate_queries(title, abstract, client)
    if not queries:
        return ""

    # Step 2+3: Search and collect results, iterating if needed
    all_papers: dict[str, ArxivPaper] = {}  # keyed by arxiv_id for dedup

    for iteration in range(_MAX_ITERATIONS):
        for query in queries:
            papers = _search_arxiv(query)
            for p in papers:
                if p.arxiv_id not in all_papers:
                    all_papers[p.arxiv_id] = p

        if not all_papers:
            break

        # Step 3: Rank results and get refinement queries
        ranked, refinement_queries = _rank_results(
            title, abstract, list(all_papers.values()), client
        )

        # Step 4: Iterate with refinement queries if provided
        if iteration < _MAX_ITERATIONS - 1 and refinement_queries:
            queries = refinement_queries
        else:
            break

    if not all_papers:
        logger.info("Literature search found no results")
        return ""

    # Step 5: Compile top results
    return _compile_context(ranked[:_TOP_K], all_papers)


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------


def search_literature(
    title: str,
    abstract: str,
    client: LLMClient,
) -> str:
    """Run the literature search. Signature unchanged for pipeline.py.

    Uses Perplexity Sonar Pro Search if OPENROUTER_API_KEY is set,
    falling back to the arXiv pipeline on failure or missing key.
    """
    if has_provider_key("openrouter"):
        try:
            result = _search_perplexity(title, abstract, client)
            logger.info("Literature search completed via Perplexity")
            return result
        except Exception:
            logger.warning("Perplexity search failed, falling back to arXiv")

    return _search_arxiv_pipeline(title, abstract, client)


def _generate_queries(title: str, abstract: str, client: LLMClient) -> list[str]:
    """Generate arXiv search queries from paper metadata."""
    messages = [
        {"role": "system", "content": ARXIV_QUERY_GEN_SYSTEM},
        {
            "role": "user",
            "content": (
                f"Generate search queries for finding related work to this paper.\n\n"
                f"**Title**: {title}\n\n"
                f"**Abstract**: {abstract[:1000]}"
            ),
        },
    ]
    try:
        result = client.complete(
            messages,
            _SearchQueries,
            max_tokens=512,
            temperature=_QUERY_GEN_TEMPERATURE,
        )
        return result.queries
    except Exception:
        logger.warning("Query generation failed, using title as fallback")
        # Fallback: use title words as a single query
        return [title]


def _rank_results(
    title: str,
    abstract: str,
    papers: list[ArxivPaper],
    client: LLMClient,
) -> tuple[list[_RankedResult], list[str]]:
    """Rank search results by relevance and suggest refinement queries."""
    results_block = "\n\n".join(
        f"- **{p.arxiv_id}**: {p.title}\n  Authors: {', '.join(p.authors[:3])}\n"
        f"  Abstract: {p.abstract[:200]}"
        for p in papers[:20]  # cap at 20 to keep prompt short
    )

    messages = [
        {"role": "system", "content": ARXIV_RANKING_SYSTEM},
        {
            "role": "user",
            "content": (
                f"**Target paper**: {title}\n"
                f"**Abstract**: {abstract[:500]}\n\n"
                f"**Search results**:\n{results_block}\n\n"
                f"Rank these results by relevance and suggest refinement queries "
                f"if important related work areas are missing."
            ),
        },
    ]
    try:
        result = client.complete(
            messages,
            _RankedResults,
            max_tokens=2048,
            temperature=_RANKING_TEMPERATURE,
        )
        ranked = sorted(result.ranked, key=lambda r: r.relevance_score, reverse=True)
        return ranked, result.refinement_queries
    except Exception:
        logger.warning("Ranking failed, returning unranked results")
        # Fallback: return all papers unranked
        unranked = [
            _RankedResult(arxiv_id=p.arxiv_id, relevance_score=0.5, reason="unranked")
            for p in papers[:_TOP_K]
        ]
        return unranked, []


def _compile_context(ranked: list[_RankedResult], papers: dict[str, ArxivPaper]) -> str:
    """Format top-ranked papers as a context block for review prompts."""
    lines = []
    for i, r in enumerate(ranked, 1):
        paper = papers.get(r.arxiv_id)
        if not paper:
            continue
        authors_str = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors_str += " et al."
        lines.append(
            f"{i}. **{paper.title}** ({authors_str}, {paper.published})\n"
            f"   arXiv:{paper.arxiv_id} — {r.reason}"
        )

    if not lines:
        return ""
    return "\n".join(lines)
