"""Pipeline orchestrator for coarse.

Runs the full review pipeline: extract -> cost gate -> structure -> agents -> synthesis.
"""

from __future__ import annotations

import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from coarse.agents.completeness import CompletenessAgent
from coarse.agents.cross_section import CrossSectionAgent
from coarse.agents.literature import search_literature
from coarse.agents.overview import OverviewAgent, merge_overview
from coarse.agents.quote_repair import QuoteRepairAgent
from coarse.agents.section import SectionAgent
from coarse.agents.verify import ProofVerifyAgent
from coarse.config import CoarseConfig, load_config
from coarse.cost import run_cost_gate
from coarse.extraction import extract_file
from coarse.llm import LLMClient
from coarse.pipeline_spec import (
    MAX_REVIEWABLE_SECTIONS,
    estimate_cross_section_count,
    estimate_section_count,
)
from coarse.progress import PipelineProgress, PipelineProgressCallback
from coarse.quote_verify import QuoteVerificationDrop, verify_quotes, verify_quotes_detailed
from coarse.review_stages import (
    _detect_section_focus,
    _review_section,
    _verify_with_fallback,
    calibrate_domain,
    extract_contribution,
    run_editorial_pass,
)
from coarse.review_stages import (
    _section_needs_proof_verify as _section_needs_proof_verify,  # noqa: F401
)
from coarse.structure import analyze_structure
from coarse.synthesis import render_review
from coarse.types import (
    DetailedComment,
    ExtractionError,
    PaperStructure,
    PaperText,
    Review,
    SectionInfo,
    SectionType,
)

logger = logging.getLogger(__name__)
_PIPELINE_FIXED_PROGRESS_STAGES = 10
_RESULTS_TYPES = {SectionType.METHODOLOGY, SectionType.RESULTS, SectionType.OTHER}
_DISCUSSION_TYPES = {SectionType.DISCUSSION, SectionType.CONCLUSION}


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


def _estimated_pipeline_stage_total(paper_text: PaperText, *, is_pdf: bool, run_qa: bool) -> int:
    """Return an initial stage total using the same section heuristics as the cost gate."""
    estimated_sections = estimate_section_count(max(0, paper_text.token_estimate))
    return (
        _PIPELINE_FIXED_PROGRESS_STAGES
        + int(is_pdf and run_qa)
        + estimated_sections
        + estimate_cross_section_count(estimated_sections)
    )


def _actual_cross_section_count(structure: PaperStructure) -> int:
    """Return how many cross-section checks this paper will actually run."""
    results_sections = [
        s for s in structure.sections if s.section_type in _RESULTS_TYPES and s.math_content
    ]
    discussion_sections = [s for s in structure.sections if s.section_type in _DISCUSSION_TYPES]
    if not results_sections or not discussion_sections:
        return 0
    return min(3, len(discussion_sections))


def _actual_pipeline_stage_total(
    *,
    is_pdf: bool,
    run_qa: bool,
    section_count: int,
    cross_section_count: int,
) -> int:
    """Return the final stage total after structure analysis resolves the paper shape."""
    return (
        _PIPELINE_FIXED_PROGRESS_STAGES
        + int(is_pdf and run_qa)
        + section_count
        + cross_section_count
    )


class _PipelineProgressReporter:
    """Best-effort adapter from pipeline milestones to callback events."""

    def __init__(
        self,
        callback: PipelineProgressCallback | None,
        *,
        total_stages: int = 1,
    ) -> None:
        self._callback = callback
        self._completed = 0
        self._total = max(1, total_stages)
        self._disabled = callback is None

    def set_total(self, total_stages: int) -> None:
        self._total = max(1, max(self._completed, total_stages))

    def start(self, stage_key: str, stage_label: str, actual_cost_usd: float) -> None:
        self._emit("started", stage_key, stage_label, actual_cost_usd)

    def complete(self, stage_key: str, stage_label: str, actual_cost_usd: float) -> None:
        self._completed += 1
        self._emit("completed", stage_key, stage_label, actual_cost_usd)

    def _emit(
        self,
        event: str,
        stage_key: str,
        stage_label: str,
        actual_cost_usd: float,
    ) -> None:
        if self._disabled or self._callback is None:
            return
        try:
            self._callback(
                PipelineProgress(
                    event=event,  # type: ignore[arg-type]
                    stage_key=stage_key,
                    stage_label=stage_label,
                    completed_stages=self._completed,
                    total_stages=self._total,
                    actual_cost_usd=actual_cost_usd,
                )
            )
        except Exception:
            logger.debug("Pipeline progress callback failed; disabling it", exc_info=True)
            self._disabled = True


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


def extract_and_structure(
    file_path: str | Path,
    client: LLMClient,
    config: CoarseConfig | None = None,
    *,
    run_qa: bool | None = None,
) -> tuple[PaperText, PaperStructure]:
    """Extract a paper and parse its structure without running any review stages.

    The non-reasoning half of ``review_paper()``: extraction, optional
    extraction QA, and structure analysis. Split out so that callers
    which want to drive review reasoning themselves can reuse it
    without pulling in the agents or the cost gate.

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


def review_paper(
    pdf_path: str | Path,
    model: str | None = None,
    skip_cost_gate: bool = False,
    config: CoarseConfig | None = None,
    author_notes: str | None = None,
    progress_callback: PipelineProgressCallback | None = None,
) -> tuple[Review, str, PaperText]:
    """Full pipeline orchestrator.

    Accepts any supported file format (PDF, TXT, MD, DOCX, TEX, HTML, EPUB).
    The ``pdf_path`` parameter name is kept for backwards compatibility.

    Args:
        pdf_path: Path to the paper file.
        model: Optional model ID override (defaults to config.default_model).
        skip_cost_gate: If True, skip the interactive cost approval prompt
            (used by the Modal worker).
        config: Optional CoarseConfig; loaded from disk when None.
        author_notes: Optional short note from the author attached to the
            submission to steer the review (e.g. "please focus on the
            identification strategy, the data section is stable"). When
            provided, it is wrapped in an ``<author_notes>`` fence and
            forwarded to every downstream review pass that shapes user-visible
            output: overview, completeness, section, proof-verify,
            cross-section, editorial, and the legacy crossref/critique
            fallback path. The notes are treated as steering input, not as
            instructions that override the review rubric. Trimmed/truncated to
            2000 chars by ``author_notes_block`` in prompts.py. ``None`` or an
            empty/ whitespace-only string is a byte-identical no-op.
        progress_callback: Optional callback receiving best-effort pipeline
            progress updates, including cumulative actual token spend.

    Pipeline order:
    1. Extract file → PaperText (format-specific extraction)
    2. Cost gate (optional)
    3. Analyze structure via markdown parsing + cheap LLM metadata → PaperStructure
    4. Phase 1: Overview, completeness, and section-context setup
    5. Phase 2: Section agents + proof verification + cross-section synthesis
    6. Editorial filtering (with legacy fallback) + quote verification/repair
    7. Synthesis → markdown

    Returns:
        (Review, markdown_string, paper_text)
    """
    if config is None:
        config = load_config()

    resolved_model = model or config.default_model
    client = LLMClient(model=resolved_model, config=config)
    progress = _PipelineProgressReporter(progress_callback)
    run_qa = False

    if skip_cost_gate:
        progress.start("extraction", "Extracting paper text", client.cost_usd)
    paper_text = extract_file(pdf_path)
    if skip_cost_gate:
        progress.complete("extraction", "Extracted paper text", client.cost_usd)

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
            if skip_cost_gate:
                progress.start("extraction_qa", "Running extraction QA", client.cost_usd)
            vision_client = LLMClient(model=config.vision_model, config=config)
            corrected = run_extraction_qa(Path(pdf_path), paper_text, vision_client)
            client.add_cost(vision_client.cost_usd)
            if corrected is not paper_text:
                # QA applied corrections — update the cache so future runs skip QA
                _save_cache(Path(pdf_path), corrected)
                logger.info("Extraction cache updated with QA corrections")
            paper_text = corrected
            if skip_cost_gate:
                progress.complete("extraction_qa", "Completed extraction QA", client.cost_usd)

    progress.set_total(_estimated_pipeline_stage_total(paper_text, is_pdf=is_pdf, run_qa=run_qa))
    gate_config = config if run_qa == config.extraction_qa else config.model_copy(
        update={"extraction_qa": run_qa}
    )

    if not skip_cost_gate:
        # Pass resolved_model so a `--model` CLI override is reflected in
        # the quote, not just in the downstream LLMClient.
        run_cost_gate(paper_text, gate_config, is_pdf=is_pdf, model=resolved_model)
        progress.complete("extraction", "Extracted paper text", client.cost_usd)
        if run_qa:
            progress.complete("extraction_qa", "Completed extraction QA", client.cost_usd)

    progress.start("structure", "Analyzing paper structure", client.cost_usd)
    structure = analyze_structure(paper_text, client)
    if not _check_extraction_quality(structure):
        raise ExtractionError(
            "Extraction failed: no sections found in markdown. "
            "The PDF may be scanned/image-only with no extractable text."
        )
    progress.complete("structure", "Analyzed paper structure", client.cost_usd)

    reviewable_sections = [
        s
        for s in structure.sections
        if s.section_type != SectionType.REFERENCES
        and (s.section_type != SectionType.APPENDIX or len(s.text) >= _MIN_APPENDIX_CHARS)
    ]
    non_ref_sections = reviewable_sections[:MAX_REVIEWABLE_SECTIONS]
    progress.set_total(
        _actual_pipeline_stage_total(
            is_pdf=is_pdf,
            run_qa=run_qa,
            section_count=len(non_ref_sections),
            cross_section_count=_actual_cross_section_count(structure),
        )
    )

    # Domain calibration + literature search + contribution extraction (parallel, all cheap)
    progress.start(
        "parallel_setup",
        "Running calibration, literature search, and contribution extraction",
        client.cost_usd,
    )
    with ThreadPoolExecutor(max_workers=3) as executor:
        cal_future = executor.submit(calibrate_domain, structure, client)
        lit_future = executor.submit(search_literature, structure.title, structure.abstract, client)
        contrib_future = executor.submit(extract_contribution, structure, client)

        calibration = cal_future.result(timeout=900)
        progress.complete("calibration", "Completed domain calibration", client.cost_usd)
        try:
            literature_context = lit_future.result(timeout=900)
        except Exception:
            logger.warning("Literature search failed, skipping", exc_info=True)
            literature_context = ""
        progress.complete("literature_search", "Completed literature search", client.cost_usd)
        contribution_context = contrib_future.result(timeout=900)
        progress.complete(
            "contribution_extraction", "Completed contribution extraction", client.cost_usd
        )

    overview_agent = OverviewAgent(client)
    section_agent = SectionAgent(client)
    quote_repair_agent = QuoteRepairAgent(client)

    # --- Phase 1: Overview (single-pass, full paper text) ---
    progress.start("overview", "Generating overview", client.cost_usd)
    overview = overview_agent.run(
        structure, calibration, literature_context, author_notes=author_notes
    )
    progress.complete("overview", "Generated overview", client.cost_usd)

    # --- Phase 1b: Completeness assessment (runs after overview, before sections) ---
    completeness_agent = CompletenessAgent(client)
    progress.start("completeness", "Checking completeness", client.cost_usd)
    try:
        completeness_issues = completeness_agent.run(
            structure,
            overview,
            calibration=calibration,
            contribution_context=contribution_context,
            author_notes=author_notes,
        )
        overview = merge_overview(overview, completeness_issues, max_total=12)
    except Exception:
        logger.warning("Completeness agent failed, skipping", exc_info=True)
    progress.complete("completeness", "Checked completeness", client.cost_usd)

    # --- Phase 2: Section agents (parallel, with verification for proof sections) ---
    verify_agent = ProofVerifyAgent(client)

    if non_ref_sections:
        progress.start("sections", "Reviewing sections", client.cost_usd)
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
                    paper_text.full_markdown,
                    structure.title,
                    overview,
                    calibration,
                    focus,
                    sec_lit,
                    structure.sections,
                    sec_abstract,
                    document_form=structure.document_form,
                    author_notes=author_notes,
                )
            )

        section_comments: list[DetailedComment] = []
        for i, future in enumerate(section_futures):
            sec_title = non_ref_sections[i].title if i < len(non_ref_sections) else "?"
            stage_label = f"Reviewed section {i + 1}/{len(non_ref_sections)}: {sec_title}"
            try:
                comments = future.result(timeout=900)
                section_comments.extend(comments)
            except Exception:
                logger.warning("Section agent failed for '%s', skipping", sec_title, exc_info=True)
                stage_label = f"Skipped section {i + 1}/{len(non_ref_sections)}: {sec_title}"
            progress.complete(f"section_{i + 1}", stage_label, client.cost_usd)

    if not section_comments:
        logger.error("All section agents failed — review will have no detailed comments")

    # --- Phase 2b: Cross-section synthesis (results ↔ discussion) ---
    results_sections = [
        s for s in structure.sections if s.section_type in _RESULTS_TYPES and s.math_content
    ]
    discussion_sections = [s for s in structure.sections if s.section_type in _DISCUSSION_TYPES]

    if results_sections and discussion_sections:
        progress.start("cross_section", "Running cross-section synthesis", client.cost_usd)
        cross_section_agent = CrossSectionAgent(client)
        main_results = results_sections[0]
        cross_section_futures = []
        selected_discussion_sections = discussion_sections[:3]
        with ThreadPoolExecutor(max_workers=3) as executor:
            for disc_sec in selected_discussion_sections:
                cross_section_futures.append(
                    executor.submit(
                        cross_section_agent.run,
                        structure.title,
                        main_results,
                        disc_sec,
                        abstract=structure.abstract,
                        document_form=structure.document_form,
                        author_notes=author_notes,
                    )
                )
            for i, future in enumerate(cross_section_futures):
                disc_sec = selected_discussion_sections[i]
                stage_label = f"Cross-checked results vs {disc_sec.title}"
                try:
                    cross_comments = future.result(timeout=900)
                    cross_comments = _verify_with_fallback(
                        cross_comments,
                        paper_text.full_markdown,
                        stage_name="Cross-section quote verification",
                        drop_unverified=False,
                    )
                    section_comments.extend(cross_comments)
                except Exception:
                    logger.warning("Cross-section synthesis failed, skipping", exc_info=True)
                    stage_label = f"Skipped cross-check vs {disc_sec.title}"
                progress.complete(f"cross_section_{i + 1}", stage_label, client.cost_usd)

    # --- Phase 3: Editorial filter (single pass — dedup + contradiction + quality) ---
    # The editorial agent receives full paper text for quote/absence verification.
    progress.start("editorial", "Running editorial filter", client.cost_usd)
    filtered_comments = run_editorial_pass(
        client,
        paper_text.full_markdown,
        overview,
        section_comments,
        title=structure.title,
        abstract=structure.abstract,
        contribution_context=contribution_context,
        document_form=structure.document_form,
        author_notes=author_notes,
    )
    progress.complete("editorial", "Completed editorial filter", client.cost_usd)

    # Programmatic quote verification against full paper text
    progress.start("quote_verification", "Verifying quotes", client.cost_usd)
    final_comments = _verify_with_repair_fallback(
        filtered_comments,
        paper_text.full_markdown,
        repair_agent=quote_repair_agent,
    )
    progress.complete("quote_verification", "Verified quotes", client.cost_usd)

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

    progress.start("synthesis", "Rendering final markdown", client.cost_usd)
    markdown = render_review(review)
    progress.complete("synthesis", "Rendered final markdown", client.cost_usd)
    return review, markdown, paper_text
