"""Pipeline orchestrator for coarse.

Runs the full review pipeline: extract -> cost gate -> structure -> agents -> synthesis.
"""
from __future__ import annotations

import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from coarse.agents.critique import CritiqueAgent
from coarse.agents.crossref import CrossrefAgent
from coarse.agents.literature import search_literature
from coarse.agents.overview import OverviewAgent
from coarse.agents.section import SectionAgent
from coarse.agents.verify import ProofVerifyAgent
from coarse.config import CoarseConfig, load_config
from coarse.cost import run_cost_gate
from coarse.extraction import extract_file
from coarse.llm import LLMClient
from coarse.prompts import CALIBRATION_SYSTEM, calibration_user
from coarse.quote_verify import verify_quotes
from coarse.structure import analyze_structure
from coarse.synthesis import render_review
from coarse.types import (
    DetailedComment,
    DomainCalibration,
    ExtractionError,
    OverviewFeedback,
    PaperStructure,
    PaperText,
    Review,
    SectionInfo,
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


_SECTION_WEIGHT = 1.5   # comments-per-section multiplier
_TOKEN_WEIGHT = 0.3     # comments-per-1k-token multiplier
_MIN_COMMENTS = 6
_MAX_COMMENTS = 25


def _compute_comment_target(structure: PaperStructure, paper_text: PaperText) -> int:
    """Compute a dynamic comment count target based on paper size.

    Formula: clamp(n_sections * _SECTION_WEIGHT + token_k * _TOKEN_WEIGHT,
                   _MIN_COMMENTS, _MAX_COMMENTS)
    where token_k = token_estimate / 1000.
    """
    n_sections = len([
        s for s in structure.sections
        if s.section_type not in (SectionType.REFERENCES, SectionType.APPENDIX)
    ])
    token_k = paper_text.token_estimate / 1000.0
    raw = n_sections * _SECTION_WEIGHT + token_k * _TOKEN_WEIGHT
    return max(_MIN_COMMENTS, min(_MAX_COMMENTS, int(round(raw))))


def _renumber_comments(comments: list[DetailedComment]) -> list[DetailedComment]:
    """Renumber comments sequentially 1..N."""
    return [c.model_copy(update={"number": i}) for i, c in enumerate(comments, start=1)]


def detect_section_focus(section: SectionInfo) -> str:
    """Detect section focus based on LLM-detected math content and section type.

    Returns one of: "proof", "methodology", "results", "literature", "general".
    The math_content flag is set during structure analysis by an LLM call.
    """
    if section.math_content:
        return "proof"
    if section.section_type == SectionType.METHODOLOGY:
        return "methodology"
    if section.section_type == SectionType.RESULTS:
        return "results"
    if section.section_type == SectionType.RELATED_WORK:
        return "literature"
    return "general"


def _review_section(
    section_agent: SectionAgent,
    verify_agent: ProofVerifyAgent,
    section: SectionInfo,
    paper_title: str,
    overview: OverviewFeedback | None,
    calibration: DomainCalibration | None,
    focus: str,
    literature_context: str,
    all_sections: list[SectionInfo],
    abstract: str,
) -> list[DetailedComment]:
    """Review a section; chain with adversarial verification for proof sections."""
    comments = section_agent.run(
        section, paper_title, overview, calibration,
        focus, literature_context,
        all_sections=all_sections, abstract=abstract,
    )
    if focus == "proof" and comments:
        comments = verify_agent.run(
            section, paper_title, comments, abstract=abstract,
        )
    return comments


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
) -> tuple[Review, str, PaperText]:
    """Full pipeline orchestrator.

    Accepts any supported file format (PDF, TXT, MD, DOCX, TEX, HTML, EPUB).
    The ``pdf_path`` parameter name is kept for backwards compatibility.

    Pipeline order:
    1. Extract file → PaperText (format-specific extraction)
    2. Cost gate (optional)
    3. Analyze structure via markdown parsing + cheap LLM metadata → PaperStructure
    4. Phase 1: Overview agent + assumption checker (parallel, blocking)
    5. Phase 2: Section agents (parallel, text-only with overview context)
    6. Cross-reference + quote verification + critique + quote re-verification
    7. Synthesis → markdown

    Returns:
        (Review, markdown_string, paper_text)
    """
    if config is None:
        config = load_config()

    resolved_model = model or config.default_model
    client = LLMClient(model=resolved_model, config=config)

    paper_text = extract_file(pdf_path)

    # Extraction QA only applies to PDFs (vision LLM compares rendered pages)
    is_pdf = Path(pdf_path).suffix.lower() == ".pdf"

    if is_pdf:
        # Auto-trigger extraction QA if garble detected or explicitly enabled
        run_qa = config.extraction_qa
        if not run_qa and paper_text.garble_ratio > 0.001:
            logger.info(
                "High garble ratio (%.4f) detected — auto-enabling extraction QA",
                paper_text.garble_ratio,
            )
            run_qa = True

        if run_qa:
            from coarse.config import resolve_api_key
            from coarse.extraction import _save_cache
            from coarse.extraction_qa import run_extraction_qa

            vision_key = resolve_api_key(config.vision_model, config)
            if vision_key is None:
                logger.warning(
                    "No API key for vision model %s — skipping extraction QA. "
                    "Set GEMINI_API_KEY or use --no-qa to silence this warning.",
                    config.vision_model,
                )
                run_qa = False

        if run_qa:
            vision_client = LLMClient(model=config.vision_model, config=config)
            corrected = run_extraction_qa(Path(pdf_path), paper_text, vision_client)
            if corrected is not paper_text:
                # QA applied corrections — update the cache so future runs skip QA
                _save_cache(Path(pdf_path), corrected)
                logger.info("Extraction cache updated with QA corrections")
            paper_text = corrected

    if not skip_cost_gate:
        run_cost_gate(paper_text, config)

    structure = analyze_structure(paper_text, client)
    if not _check_extraction_quality(structure):
        raise ExtractionError(
            "Extraction failed: no sections found in markdown. "
            "The PDF may be scanned/image-only with no extractable text."
        )

    # Domain calibration + literature search (parallel, both cheap)
    with ThreadPoolExecutor(max_workers=2) as executor:
        cal_future = executor.submit(calibrate_domain, structure, client)
        lit_future = executor.submit(
            search_literature, structure.title, structure.abstract, client
        )

        calibration = cal_future.result(timeout=900)
        try:
            literature_context = lit_future.result(timeout=900)
        except Exception:
            logger.warning("Literature search failed, skipping")
            literature_context = ""

    # Compute dynamic comment target based on paper size
    comment_target = _compute_comment_target(structure, paper_text)

    overview_agent = OverviewAgent(client)
    section_agent = SectionAgent(client)
    crossref_agent = CrossrefAgent(client)

    # Review all sections except references; skip very short appendices.
    # Cap at 25 sections to keep total comment count manageable for crossref.
    _MIN_APPENDIX_CHARS = 500

    reviewable_sections = [
        s for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX
             or len(s.text) >= _MIN_APPENDIX_CHARS)
    ]
    non_ref_sections = reviewable_sections[:25]

    # --- Phase 1: Multi-judge overview panel (blocking) ---
    # Assumption checking is folded into the methodology overview persona.
    overview = overview_agent.run_panel(structure, calibration, literature_context)

    # --- Phase 2: Section agents (parallel, with verification for proof sections) ---
    verify_agent = ProofVerifyAgent(client)

    with ThreadPoolExecutor(max_workers=10) as executor:
        section_futures = []
        # Only pass literature context to sections that benefit from it
        _LIT_RELEVANT = {SectionType.INTRODUCTION, SectionType.RELATED_WORK}
        for section in non_ref_sections:
            focus = detect_section_focus(section)
            sec_lit = literature_context if (
                section.section_type in _LIT_RELEVANT or focus == "literature"
            ) else ""
            sec_abstract = structure.abstract if focus == "proof" else ""
            section_futures.append(
                executor.submit(
                    _review_section,
                    section_agent, verify_agent, section, structure.title,
                    overview, calibration, focus, sec_lit,
                    structure.sections, sec_abstract,
                )
            )

        section_comments: list[DetailedComment] = []
        for i, future in enumerate(section_futures):
            try:
                comments = future.result(timeout=900)
                section_comments.extend(comments)
            except Exception:
                sec_title = non_ref_sections[i].title if i < len(non_ref_sections) else "?"
                logger.warning("Section agent failed for '%s', skipping", sec_title)

    if not section_comments:
        logger.error("All section agents failed — review will have no detailed comments")

    try:
        deduped_comments = crossref_agent.run(
            overview, section_comments, comment_target=comment_target
        )
    except Exception:
        logger.warning("Crossref agent failed, using raw section comments")
        deduped_comments = section_comments

    # Final quote verification against full paper text
    verified_comments = verify_quotes(
        deduped_comments, paper_text.full_markdown, drop_unverified=True,
    )
    if deduped_comments and not verified_comments:
        logger.warning("Quote verification dropped ALL comments — skipping verification")
        verified_comments = deduped_comments

    critique_agent = CritiqueAgent(client)
    try:
        final_comments = critique_agent.run(
            overview, verified_comments, comment_target=comment_target
        )
    except Exception:
        logger.warning("Critique agent failed, using verified comments")
        final_comments = verified_comments

    # Re-verify quotes after critique (critique re-emits through JSON, re-garbling LaTeX)
    final_comments_pre_verify = final_comments
    final_comments = verify_quotes(
        final_comments, paper_text.full_markdown, drop_unverified=True,
    )
    if final_comments_pre_verify and not final_comments:
        logger.warning("Quote verification dropped ALL comments — skipping verification")
        final_comments = final_comments_pre_verify

    # Ensure sequential numbering 1..N
    final_comments = _renumber_comments(final_comments)

    review = Review(
        title=structure.title,
        domain=structure.domain,
        taxonomy=structure.taxonomy,
        date=datetime.date.today().strftime("%m/%d/%Y"),
        overall_feedback=overview,
        detailed_comments=final_comments,
    )

    markdown = render_review(review)
    return review, markdown, paper_text
