"""Pipeline orchestrator for coarse.

Runs the full review pipeline: extract -> cost gate -> structure -> agents -> synthesis.
"""
from __future__ import annotations

import datetime
import logging
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

logger = logging.getLogger(__name__)


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

    # Review main body sections only: skip references, appendix, and empty sections.
    # Cap at 25 sections to keep total comment count manageable for crossref.
    reviewable_sections = [
        s for s in structure.sections
        if s.section_type not in (SectionType.REFERENCES, SectionType.APPENDIX)
        and len(s.text) > 50
    ]
    non_ref_sections = reviewable_sections[:25]

    # NOTE: LLMClient._cost_usd is incremented without a lock across threads;
    # this is a benign data race for advisory cost tracking only.
    with ThreadPoolExecutor(max_workers=10) as executor:
        overview_future = executor.submit(overview_agent.run, structure)
        # Pass paper_text to section agent so it can include page images in vision mode
        has_images = any(p.image_b64 for p in paper_text.pages)
        pt_for_sections = paper_text if has_images else None
        section_futures = [
            executor.submit(section_agent.run, section, structure.title, pt_for_sections)
            for section in non_ref_sections
        ]

        overview = overview_future.result()
        section_comments: list[DetailedComment] = []
        for i, future in enumerate(section_futures):
            try:
                section_comments.extend(future.result())
            except Exception:
                sec_title = non_ref_sections[i].title if i < len(non_ref_sections) else "?"
                logger.warning("Section agent failed for '%s', skipping", sec_title)

    # Cap comments sent to crossref to avoid output token overflow.
    if len(section_comments) > 50:
        logger.info("Capping %d section comments to 50 for crossref", len(section_comments))
        section_comments = section_comments[:50]

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
