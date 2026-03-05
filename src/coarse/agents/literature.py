"""Literature search agent — finds related papers on arXiv to ground the review.

Uses the arXiv API (free, no auth) with an agentic loop:
1. Generate search queries from paper title/abstract (LLM call)
2. Search arXiv API
3. Rank results for relevance (LLM call)
4. Optionally refine queries and re-search
5. Compile top results as structured context
"""
from __future__ import annotations

import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from pydantic import BaseModel, Field

from coarse.llm import LLMClient

logger = logging.getLogger(__name__)

_ARXIV_API = "http://export.arxiv.org/api/query"
_MAX_RESULTS_PER_QUERY = 10
_MAX_ITERATIONS = 2
_TOP_K = 8

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
# arXiv API helpers (stdlib only)
# ---------------------------------------------------------------------------

def _search_arxiv(query: str, max_results: int = _MAX_RESULTS_PER_QUERY) -> list[ArxivPaper]:
    """Search arXiv API and parse Atom XML response."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
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
            name.text.strip()
            for name in entry.findall("atom:author/atom:name", _NS)
            if name.text
        ]

        published = entry.findtext("atom:published", default="", namespaces=_NS)[:10]

        if title:
            papers.append(ArxivPaper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract[:500],
                published=published,
            ))

    return papers


# ---------------------------------------------------------------------------
# LLM prompt templates
# ---------------------------------------------------------------------------

_QUERY_GEN_SYSTEM = """\
You are a research librarian. Given a paper's title and abstract, generate 3-5 \
diverse search queries for finding related work on arXiv. Include:
- The paper's core method/technique
- The application domain
- Key theoretical concepts
- Alternative approaches to the same problem
Keep queries concise (3-8 words each).
"""

_RANKING_SYSTEM = """\
You are a research relevance assessor. Given a target paper and a list of arXiv \
search results, score each result's relevance (0.0-1.0) to the target paper.

Score 0.8-1.0: Directly related — same method, same problem, or a paper the \
target likely cites or should cite.
Score 0.5-0.7: Moderately related — related technique or application domain.
Score 0.0-0.4: Tangentially related or irrelevant.

Also suggest 0-3 refinement queries if important areas of related work are missing.
"""


# ---------------------------------------------------------------------------
# Main agent
# ---------------------------------------------------------------------------

def search_literature(
    title: str,
    abstract: str,
    client: LLMClient,
) -> str:
    """Run the literature search agentic loop.

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


def _generate_queries(title: str, abstract: str, client: LLMClient) -> list[str]:
    """Generate arXiv search queries from paper metadata."""
    messages = [
        {"role": "system", "content": _QUERY_GEN_SYSTEM},
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
        result = client.complete(messages, _SearchQueries, max_tokens=512, temperature=0.5)
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
        {"role": "system", "content": _RANKING_SYSTEM},
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
        result = client.complete(messages, _RankedResults, max_tokens=2048, temperature=0.2)
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
