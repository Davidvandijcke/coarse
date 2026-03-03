"""Pipeline orchestrator for coarse.

Runs the full review pipeline: extract -> cost gate -> structure -> agents -> synthesis.
"""
from __future__ import annotations

import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from coarse.agents.critique import CritiqueAgent
from coarse.agents.crossref import CrossrefAgent
from coarse.agents.overview import OverviewAgent
from coarse.agents.section import SectionAgent
from coarse.config import CoarseConfig, load_config
from coarse.cost import run_cost_gate
from coarse.extraction import extract_text
from coarse.llm import LLMClient
from coarse.structure import analyze_structure
from coarse.synthesis import render_review
from coarse.types import DetailedComment, Review, SectionType


def review_paper(
    pdf_path: str | Path,
    model: str | None = None,
    vision: bool = False,
    skip_cost_gate: bool = False,
    config: CoarseConfig | None = None,
) -> tuple[Review, str]:
    """Full pipeline orchestrator.

    Extracts PDF, runs cost gate, analyzes structure, runs overview + section agents
    in parallel, then crossref, critique, and synthesis.

    Returns:
        (Review, markdown_string)
    """
    if config is None:
        config = load_config()

    resolved_model = model or config.default_model
    client = LLMClient(model=resolved_model, config=config)

    paper_text = extract_text(pdf_path, vision=vision)

    if not skip_cost_gate:
        run_cost_gate(paper_text, config)

    structure = analyze_structure(paper_text, client)

    overview_agent = OverviewAgent(client)
    section_agent = SectionAgent(client)
    crossref_agent = CrossrefAgent(client)
    critique_agent = CritiqueAgent(client)

    non_ref_sections = [
        s for s in structure.sections if s.section_type != SectionType.REFERENCES
    ]

    # NOTE: LLMClient._cost_usd is incremented without a lock across threads;
    # this is a benign data race for advisory cost tracking only.
    with ThreadPoolExecutor(max_workers=10) as executor:
        overview_future = executor.submit(overview_agent.run, structure)
        section_futures = [
            executor.submit(section_agent.run, section, structure.title)
            for section in non_ref_sections
        ]

        overview = overview_future.result()
        section_comments: list[DetailedComment] = []
        for future in section_futures:
            section_comments.extend(future.result())

    deduped_comments = crossref_agent.run(paper_text, overview, section_comments)
    final_comments = critique_agent.run(overview, deduped_comments)

    review = Review(
        title=structure.title,
        domain=structure.domain,
        taxonomy=structure.taxonomy,
        date=datetime.date.today().strftime("%m/%d/%Y"),
        overall_feedback=overview,
        detailed_comments=final_comments,
    )

    markdown = render_review(review)
    return review, markdown
