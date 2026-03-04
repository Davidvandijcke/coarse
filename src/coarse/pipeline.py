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
from coarse.agents.overview import OverviewAgent, check_assumptions, merge_overview
from coarse.agents.section import SectionAgent
from coarse.config import CoarseConfig, load_config
from coarse.cost import run_cost_gate
from coarse.extraction import extract_text
from coarse.llm import LLMClient
from coarse.prompts import CALIBRATION_SYSTEM, calibration_user
from coarse.quote_verify import verify_quotes
from coarse.structure import analyze_structure
from coarse.synthesis import render_review
from coarse.types import (
    DetailedComment,
    DomainCalibration,
    ExtractionError,
    PaperStructure,
    PaperText,
    Review,
    SectionType,
)

logger = logging.getLogger(__name__)


def _check_extraction_quality(structure: "PaperStructure") -> bool:
    """Check whether extraction produced usable output.

    Returns True if sections exist with non-empty text.
    """
    if not structure.sections:
        logger.warning("No sections extracted from markdown.")
        return False

    return True


_PROOF_KEYWORDS = frozenset([
    "theorem", "proof", "lemma", "proposition", "corollary", "q.e.d", "qed",
    "∎", "□", "we prove", "we show that", "it follows that",
])


def detect_section_focus(section: "SectionInfo") -> str:
    """Detect whether a section contains proofs, methodology, literature, etc.

    Returns one of: "proof", "methodology", "literature", "general".
    """
    text_lower = section.text.lower()
    if any(kw in text_lower for kw in _PROOF_KEYWORDS):
        return "proof"
    if section.section_type == SectionType.METHODOLOGY:
        return "methodology"
    if section.section_type == SectionType.RELATED_WORK:
        return "literature"
    return "general"


def calibrate_domain(
    structure: PaperStructure, client: LLMClient
) -> DomainCalibration | None:
    """Generate domain-specific review criteria from the paper's content.

    Single cheap LLM call (~$0.02). Returns None on failure (fallback to generic).
    """
    section_titles = ", ".join(
        f"{s.number}. {s.title}" for s in structure.sections
    )
    messages = [
        {"role": "system", "content": CALIBRATION_SYSTEM},
        {
            "role": "user",
            "content": calibration_user(
                structure.title, structure.domain,
                structure.abstract, section_titles,
            ),
        },
    ]
    try:
        return client.complete(messages, DomainCalibration, max_tokens=2048, temperature=0.3)
    except Exception:
        logger.warning("Domain calibration failed, using generic prompts")
        return None


def review_paper(
    pdf_path: str | Path,
    model: str | None = None,
    skip_cost_gate: bool = False,
    config: CoarseConfig | None = None,
) -> tuple[Review, str]:
    """Full pipeline orchestrator.

    Pipeline order:
    1. Extract PDF → PaperText (Docling markdown)
    2. Cost gate (optional)
    3. Analyze structure via markdown parsing + cheap LLM metadata → PaperStructure
    4. Phase 1: Overview agent + assumption checker (parallel, blocking)
    5. Phase 2: Section agents (parallel, text-only with overview context)
    6. Cross-reference + critique
    7. Synthesis → markdown

    Returns:
        (Review, markdown_string)
    """
    if config is None:
        config = load_config()

    resolved_model = model or config.default_model
    client = LLMClient(model=resolved_model, config=config)

    paper_text = extract_text(pdf_path)

    if not skip_cost_gate:
        run_cost_gate(paper_text, config)

    structure = analyze_structure(paper_text, client)
    if not _check_extraction_quality(structure):
        raise ExtractionError(
            "Extraction failed: no sections found in markdown. "
            "The PDF may be scanned/image-only with no extractable text."
        )

    # Domain calibration: generate domain-specific review criteria
    calibration = calibrate_domain(structure, client)

    overview_agent = OverviewAgent(client)
    section_agent = SectionAgent(client)
    crossref_agent = CrossrefAgent(client)
    critique_agent = CritiqueAgent(client)

    # Review main body sections only: skip references/appendix.
    # Cap at 25 sections to keep total comment count manageable for crossref.
    reviewable_sections = [
        s for s in structure.sections
        if s.section_type not in (SectionType.REFERENCES, SectionType.APPENDIX)
    ]
    non_ref_sections = reviewable_sections[:25]

    # --- Phase 1: Multi-judge overview panel + assumption checker (blocking) ---
    with ThreadPoolExecutor(max_workers=2) as executor:
        overview_future = executor.submit(
            overview_agent.run_panel, structure, calibration
        )
        assumption_future = executor.submit(
            check_assumptions, structure, client, calibration
        )

        overview = overview_future.result()
        try:
            assumption_issues = assumption_future.result()
        except Exception:
            logger.warning("Assumption checker failed, skipping")
            assumption_issues = []

    overview = merge_overview(overview, assumption_issues)

    # --- Phase 2: Section agents (parallel, text-only with overview context) ---
    with ThreadPoolExecutor(max_workers=10) as executor:
        section_futures = [
            executor.submit(
                section_agent.run, section, structure.title,
                overview, calibration,
                detect_section_focus(section),
            )
            for section in non_ref_sections
        ]

        section_comments: list[DetailedComment] = []
        for i, future in enumerate(section_futures):
            try:
                comments = future.result()
                section_comments.extend(comments)
            except Exception:
                sec_title = non_ref_sections[i].title if i < len(non_ref_sections) else "?"
                logger.warning("Section agent failed for '%s', skipping", sec_title)

    # Cap comments sent to crossref to avoid output token overflow.
    if len(section_comments) > 50:
        logger.info("Capping %d section comments to 50 for crossref", len(section_comments))
        section_comments = section_comments[:50]

    deduped_comments = crossref_agent.run(paper_text, overview, section_comments)
    # Final quote verification against full paper text
    verified_comments = verify_quotes(deduped_comments, paper_text.full_markdown, drop_unverified=True)
    final_comments = critique_agent.run(overview, verified_comments)

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
