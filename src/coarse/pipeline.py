"""Pipeline orchestrator for coarse.

Runs the full review pipeline: extract -> cost gate -> structure -> agents -> synthesis.
"""

from __future__ import annotations

import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from coarse.agents.completeness import CompletenessAgent
from coarse.agents.critique import CritiqueAgent
from coarse.agents.cross_section import CrossSectionAgent
from coarse.agents.crossref import CrossrefAgent
from coarse.agents.editorial import EditorialAgent
from coarse.agents.literature import search_literature
from coarse.agents.overview import OverviewAgent, merge_overview
from coarse.agents.quote_repair import QuoteRepairAgent
from coarse.agents.section import SectionAgent
from coarse.agents.verify import ProofVerifyAgent
from coarse.config import CoarseConfig, load_config
from coarse.cost import run_cost_gate
from coarse.extraction import extract_file
from coarse.llm import LLMClient
from coarse.models import STAGE_MODELS
from coarse.prompts import (
    CALIBRATION_SYSTEM,
    CONTRIBUTION_EXTRACTION_SYSTEM,
    calibration_user,
    contribution_extraction_user,
)
from coarse.quote_verify import QuoteVerificationDrop, verify_quotes, verify_quotes_detailed
from coarse.routing import StageRouter
from coarse.structure import analyze_structure
from coarse.synthesis import render_review
from coarse.types import (
    ContributionContext,
    DetailedComment,
    DocumentForm,
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

    Returns True if sections exist with sufficient text content.
    """
    if not structure.sections:
        logger.warning("No sections extracted from markdown.")
        return False

    total_text = sum(len(s.text) for s in structure.sections)
    if total_text < 500:
        logger.warning(
            "Extraction produced only %d chars of section text (minimum: 500).",
            total_text,
        )
        return False

    return True


def _verify_with_fallback(
    comments: list["DetailedComment"],
    paper_markdown: str,
) -> list["DetailedComment"]:
    """Run quote verification, falling back to originals if all are dropped."""
    verified = verify_quotes(comments, paper_markdown, drop_unverified=True)
    if comments and not verified:
        logger.warning("Quote verification dropped ALL comments — skipping verification")
        return comments
    return verified


_QUOTE_REPAIR_RATIO_FLOOR = 0.65
_QUOTE_REPAIR_MATH_RATIO_FLOOR = 0.75


def _should_attempt_quote_repair(drop: QuoteVerificationDrop) -> bool:
    """Return True iff a dropped comment is a plausible quote-repair candidate."""
    floor = _QUOTE_REPAIR_MATH_RATIO_FLOOR if drop.math_heavy else _QUOTE_REPAIR_RATIO_FLOOR
    return drop.ratio >= floor and bool(drop.candidate_passages)


def _repair_quotes_with_agent(
    dropped: list[QuoteVerificationDrop],
    paper_markdown: str,
    repair_agent: QuoteRepairAgent,
) -> list[DetailedComment]:
    """Ask the LLM to re-anchor plausible dropped comments, then re-verify."""
    candidates = [drop for drop in dropped if _should_attempt_quote_repair(drop)]
    if not candidates:
        return []

    payload = [
        {
            "number": drop.comment.number,
            "title": drop.comment.title,
            "feedback": drop.comment.feedback,
            "original_quote": drop.comment.quote,
            "candidate_passages": drop.candidate_passages,
            "ratio": drop.ratio,
            "threshold": drop.threshold,
        }
        for drop in candidates
    ]

    try:
        repaired_map = repair_agent.run(payload)
    except Exception:
        logger.warning("Quote repair agent failed, skipping salvage", exc_info=True)
        return []

    repaired_comments: list[DetailedComment] = []
    for drop in candidates:
        repaired_quote = repaired_map.get(drop.comment.number, "").strip()
        if not repaired_quote or repaired_quote == drop.comment.quote:
            continue
        repaired_comments.append(drop.comment.model_copy(update={"quote": repaired_quote}))

    if not repaired_comments:
        return []

    repaired_verified = verify_quotes(repaired_comments, paper_markdown, drop_unverified=True)
    if repaired_verified:
        logger.info("Quote repair salvaged %d comments", len(repaired_verified))
    return repaired_verified


def _verify_with_repair_fallback(
    comments: list[DetailedComment],
    paper_markdown: str,
    repair_agent: QuoteRepairAgent | None = None,
) -> list[DetailedComment]:
    """Run deterministic quote verification, then bounded batched repair."""
    verification = verify_quotes_detailed(comments, paper_markdown, drop_unverified=True)
    verified_map = {comment.number: comment for comment in verification.verified_comments}

    if repair_agent and verification.dropped_comments:
        repaired = _repair_quotes_with_agent(
            verification.dropped_comments,
            paper_markdown,
            repair_agent,
        )
        for comment in repaired:
            verified_map[comment.number] = comment

    ordered = [verified_map[c.number] for c in comments if c.number in verified_map]
    if comments and not ordered:
        logger.warning("Quote verification dropped ALL comments — skipping verification")
        return comments
    return ordered


def _verify_section_with_fallback(
    comments: list["DetailedComment"],
    section: SectionInfo,
) -> list["DetailedComment"]:
    """Verify quotes against the local section text before global verification."""
    verified = verify_quotes(comments, section.text, drop_unverified=True)
    if comments and not verified:
        logger.warning(
            "Section-local quote verification dropped ALL comments for section %s (%s) "
            "— keeping originals",
            section.number,
            section.title,
        )
        return comments
    return verified


_MIN_APPENDIX_CHARS = 500  # skip appendix sections shorter than this


def _renumber_comments(comments: list[DetailedComment]) -> list[DetailedComment]:
    """Renumber comments sequentially 1..N."""
    return [c.model_copy(update={"number": i}) for i, c in enumerate(comments, start=1)]


def _detect_section_focus(section: SectionInfo) -> str:
    """Detect section focus based on LLM-detected math content and section type.

    Returns one of: "proof", "methodology", "results", "literature", "discussion", "general".
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
    if section.section_type in (SectionType.DISCUSSION, SectionType.CONCLUSION):
        return "discussion"
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
    document_form: DocumentForm = "manuscript",
) -> list[DetailedComment]:
    """Review a section; chain with adversarial verification for proof sections."""
    comments = section_agent.run(
        section,
        paper_title,
        overview,
        calibration,
        focus,
        literature_context,
        all_sections=all_sections,
        abstract=abstract,
        document_form=document_form,
    )
    if focus == "proof" and comments:
        comments = verify_agent.run(
            section,
            paper_title,
            comments,
            abstract=abstract,
            document_form=document_form,
        )
    return _verify_section_with_fallback(comments, section)


def extract_and_structure(
    file_path: str | Path,
    client: LLMClient,
    config: CoarseConfig | None = None,
    *,
    run_qa: bool | None = None,
) -> tuple[PaperText, PaperStructure]:
    """Extract a paper and parse its structure without running any review stages.

    The non-reasoning half of ``review_paper()``: extraction, optional
    extraction QA, and structure analysis. Callers that want to drive the
    review reasoning themselves — e.g. the MCP server at
    ``deploy/mcp_server.py`` — reuse this helper without pulling in the
    agents or the cost gate.

    Raises ExtractionError if extraction produces no usable sections.
    """
    if config is None:
        config = load_config()

    paper_text = extract_file(file_path)

    is_pdf = Path(file_path).suffix.lower() == ".pdf"
    if is_pdf:
        should_qa = run_qa if run_qa is not None else config.extraction_qa
        if not should_qa and paper_text.garble_ratio > 0.001:
            logger.info(
                "High garble ratio (%.4f) detected — auto-enabling extraction QA",
                paper_text.garble_ratio,
            )
            should_qa = True

        if should_qa:
            from coarse.config import resolve_api_key
            from coarse.extraction import _save_cache
            from coarse.extraction_qa import run_extraction_qa

            vision_key = resolve_api_key(config.vision_model, config)
            if vision_key is None:
                logger.warning(
                    "No API key for vision model %s — skipping extraction QA",
                    config.vision_model,
                )
            else:
                vision_client = LLMClient(model=config.vision_model, config=config)
                corrected = run_extraction_qa(Path(file_path), paper_text, vision_client)
                if corrected is not paper_text:
                    _save_cache(Path(file_path), corrected)
                    logger.info("Extraction cache updated with QA corrections")
                paper_text = corrected

    structure = analyze_structure(paper_text, client)
    if not _check_extraction_quality(structure):
        raise ExtractionError(
            "Extraction failed: no sections found. "
            "The file may be scanned/image-only with no extractable text."
        )
    return paper_text, structure


def calibrate_domain(structure: PaperStructure, client: LLMClient) -> DomainCalibration | None:
    """Generate domain-specific review criteria from the paper's content.

    Single cheap LLM call (~$0.02). Returns None on failure (fallback to generic).
    """
    section_titles = ", ".join(f"{s.number}. {s.title}" for s in structure.sections)
    messages = [
        {"role": "system", "content": CALIBRATION_SYSTEM},
        {
            "role": "user",
            "content": calibration_user(
                structure.title,
                structure.domain,
                structure.abstract,
                section_titles,
            ),
        },
    ]
    try:
        return client.complete(messages, DomainCalibration, max_tokens=2048, temperature=0.3)
    except Exception:
        logger.warning("Domain calibration failed, using generic prompts", exc_info=True)
        return None


def extract_contribution(
    structure: PaperStructure,
    client: LLMClient,
) -> ContributionContext | None:
    """Extract paper's stated contributions via cheap LLM call (~$0.02).

    Returns None on failure (pipeline proceeds without contribution context).
    """
    intro_text = ""
    conclusion_text = ""
    for s in structure.sections:
        if s.section_type == SectionType.INTRODUCTION:
            intro_text = s.text
        elif s.section_type == SectionType.CONCLUSION:
            conclusion_text = s.text

    if not intro_text:
        intro_text = structure.abstract

    messages = [
        {"role": "system", "content": CONTRIBUTION_EXTRACTION_SYSTEM},
        {
            "role": "user",
            "content": contribution_extraction_user(
                structure.title,
                structure.abstract,
                intro_text,
                conclusion_text,
            ),
        },
    ]
    try:
        return client.complete(messages, ContributionContext, max_tokens=2048, temperature=0.2)
    except Exception:
        logger.warning("Contribution extraction failed, proceeding without", exc_info=True)
        return None


def review_paper(
    pdf_path: str | Path,
    model: str | None = None,
    skip_cost_gate: bool = False,
    config: CoarseConfig | None = None,
    stage_overrides: dict[str, str] | None = None,
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

    Args:
        pdf_path: Input file path.
        model: Optional explicit base model override (``--model`` CLI flag).
        skip_cost_gate: Skip the interactive cost-confirmation prompt.
        config: Pre-loaded config, else loaded from ``~/.coarse/config.toml``.
        stage_overrides: Optional per-stage model overrides, merged on top
            of the default ``STAGE_MODELS`` map. Keys must be valid stage
            names from ``coarse.routing.STAGE_NAMES``. Used by the CLI's
            ``--stage-override`` flag and by tests.

    Returns:
        (Review, markdown_string, paper_text)
    """
    if config is None:
        config = load_config()

    resolved_model = model or config.default_model
    router = StageRouter(
        base_model=resolved_model,
        overrides={**STAGE_MODELS, **(stage_overrides or {})},
        config=config,
    )

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
        # Pass resolved_model + stage_overrides so the cost quote reflects
        # both the user's --model flag and any per-stage --stage-override
        # overrides, matching what the router will actually execute.
        run_cost_gate(
            paper_text,
            config,
            is_pdf=is_pdf,
            model=resolved_model,
            stage_overrides=stage_overrides,
        )

    structure = analyze_structure(
        paper_text,
        router.client_for("metadata"),
        math_client=router.client_for("math_detection"),
    )
    if not _check_extraction_quality(structure):
        raise ExtractionError(
            "Extraction failed: no sections found in markdown. "
            "The PDF may be scanned/image-only with no extractable text."
        )

    # Domain calibration + literature search + contribution extraction (parallel, all cheap)
    with ThreadPoolExecutor(max_workers=3) as executor:
        cal_future = executor.submit(
            calibrate_domain,
            structure,
            router.client_for("calibration"),
        )
        lit_future = executor.submit(
            search_literature,
            structure.title,
            structure.abstract,
            router.client_for("overview"),
        )
        contrib_future = executor.submit(
            extract_contribution,
            structure,
            router.client_for("contribution_extraction"),
        )

        calibration = cal_future.result(timeout=900)
        try:
            literature_context = lit_future.result(timeout=900)
        except Exception:
            logger.warning("Literature search failed, skipping", exc_info=True)
            literature_context = ""
        contribution_context = contrib_future.result(timeout=900)

    overview_agent = OverviewAgent(router.client_for("overview"))
    section_agent = SectionAgent(router.client_for("section"))
    editorial_agent = EditorialAgent(router.client_for("editorial"))
    quote_repair_agent = QuoteRepairAgent(router.client_for("editorial"))

    reviewable_sections = [
        s
        for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX or len(s.text) >= _MIN_APPENDIX_CHARS)
    ]
    non_ref_sections = reviewable_sections[:25]

    # --- Phase 1: Overview (single-pass, full paper text) ---
    overview = overview_agent.run(structure, calibration, literature_context)

    # --- Phase 1b: Completeness assessment (runs after overview, before sections) ---
    completeness_agent = CompletenessAgent(router.client_for("completeness"))
    try:
        completeness_issues = completeness_agent.run(
            structure,
            overview,
            calibration=calibration,
            contribution_context=contribution_context,
        )
        overview = merge_overview(overview, completeness_issues, max_total=12)
    except Exception:
        logger.warning("Completeness agent failed, skipping", exc_info=True)

    # --- Phase 2: Section agents (parallel, with verification for proof sections) ---
    verify_agent = ProofVerifyAgent(router.client_for("verify"))

    with ThreadPoolExecutor(max_workers=10) as executor:
        section_futures = []
        # Only pass literature context to sections that benefit from it
        _LIT_RELEVANT = {SectionType.INTRODUCTION, SectionType.RELATED_WORK}
        for section in non_ref_sections:
            focus = _detect_section_focus(section)
            sec_lit = (
                literature_context
                if (section.section_type in _LIT_RELEVANT or focus == "literature")
                else ""
            )
            sec_abstract = structure.abstract
            section_futures.append(
                executor.submit(
                    _review_section,
                    section_agent,
                    verify_agent,
                    section,
                    structure.title,
                    overview,
                    calibration,
                    focus,
                    sec_lit,
                    structure.sections,
                    sec_abstract,
                    structure.document_form,
                )
            )

        section_comments: list[DetailedComment] = []
        for i, future in enumerate(section_futures):
            try:
                comments = future.result(timeout=900)
                section_comments.extend(comments)
            except Exception:
                sec_title = non_ref_sections[i].title if i < len(non_ref_sections) else "?"
                logger.warning("Section agent failed for '%s', skipping", sec_title, exc_info=True)

    if not section_comments:
        logger.error("All section agents failed — review will have no detailed comments")

    # --- Phase 2b: Cross-section synthesis (results ↔ discussion) ---
    _RESULTS_TYPES = {SectionType.METHODOLOGY, SectionType.RESULTS, SectionType.OTHER}
    _DISCUSSION_TYPES = {SectionType.DISCUSSION, SectionType.CONCLUSION}

    results_sections = [
        s for s in structure.sections if s.section_type in _RESULTS_TYPES and s.math_content
    ]
    discussion_sections = [s for s in structure.sections if s.section_type in _DISCUSSION_TYPES]

    if results_sections and discussion_sections:
        cross_section_agent = CrossSectionAgent(router.client_for("cross_section"))
        main_results = results_sections[0]
        cross_section_futures = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            for disc_sec in discussion_sections[:3]:
                cross_section_futures.append(
                    executor.submit(
                        cross_section_agent.run,
                        structure.title,
                        main_results,
                        disc_sec,
                        abstract=structure.abstract,
                        document_form=structure.document_form,
                    )
                )
            for future in cross_section_futures:
                try:
                    cross_comments = future.result(timeout=900)
                    section_comments.extend(cross_comments)
                except Exception:
                    logger.warning("Cross-section synthesis failed, skipping", exc_info=True)

    # --- Phase 3: Editorial filter (single pass — dedup + contradiction + quality) ---
    # The editorial agent receives full paper text for quote/absence verification.
    try:
        filtered_comments = editorial_agent.run(
            paper_text.full_markdown,
            overview,
            section_comments,
            title=structure.title,
            abstract=structure.abstract,
            contribution_context=contribution_context,
            document_form=structure.document_form,
        )
    except Exception:
        # Fallback: use legacy crossref → critique pipeline if editorial agent fails.
        # Route both legacy agents through the "editorial" stage slot since
        # they occupy the same functional position in the pipeline.
        logger.warning("Editorial agent failed, falling back to crossref+critique", exc_info=True)
        crossref_agent = CrossrefAgent(router.client_for("editorial"))
        critique_agent = CritiqueAgent(router.client_for("editorial"))
        try:
            filtered_comments = crossref_agent.run(
                overview,
                section_comments,
                title=structure.title,
                abstract=structure.abstract,
            )
        except Exception:
            logger.warning("Crossref fallback also failed", exc_info=True)
            filtered_comments = section_comments
        try:
            filtered_comments = critique_agent.run(
                overview,
                filtered_comments,
                title=structure.title,
                abstract=structure.abstract,
            )
        except Exception:
            logger.warning("Critique fallback also failed", exc_info=True)

    # Programmatic quote verification against full paper text
    final_comments = _verify_with_repair_fallback(
        filtered_comments,
        paper_text.full_markdown,
        repair_agent=quote_repair_agent,
    )

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
