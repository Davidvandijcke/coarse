"""Stage-local review helpers used by the pipeline orchestrator."""

from __future__ import annotations

import logging

from coarse.agents.critique import CritiqueAgent
from coarse.agents.crossref import CrossrefAgent
from coarse.agents.editorial import EditorialAgent
from coarse.agents.section import SectionAgent
from coarse.agents.verify import ProofVerifyAgent
from coarse.llm import LLMClient
from coarse.pipeline_spec import MAX_REVIEWABLE_SECTIONS
from coarse.prompts import (
    CALIBRATION_SYSTEM,
    CONTRIBUTION_EXTRACTION_SYSTEM,
    calibration_user,
    contribution_extraction_user,
)
from coarse.quote_verify import verify_quotes
from coarse.types import (
    ContributionContext,
    DetailedComment,
    DocumentForm,
    DomainCalibration,
    OverviewFeedback,
    PaperStructure,
    SectionInfo,
    SectionType,
)

logger = logging.getLogger(__name__)

_MIN_APPENDIX_CHARS = 500  # skip appendix sections shorter than this

# Weight applied to a mathematical section's length when the cap binds. A
# proof is worth more per character than prose, but not infinitely more:
# ranking all math ahead of all prose dropped a 5.6k-character numerical
# appendix in favour of a 551-character proof of a corollary. Blending keeps a
# long prose appendix competitive with a short proof.
_MATH_SECTION_WEIGHT = 2.5

# Section titles that are never worth reviewing. Matched case-insensitively
# against the start of the title. The reference list is frequently absorbed
# into "Acknowledgements" by the heading parser, so that section can be very
# long without containing anything reviewable.
# Longest a heading can be and still be one of the boilerplate sections below
# rather than a substantive section that happens to start with the same word.
_MAX_BOILERPLATE_TITLE_CHARS = 40

_SKIP_TITLE_PREFIXES = (
    "acknowledgement",
    "acknowledgment",
    "references",
    "bibliography",
    "funding",
    "conflict of interest",
    "data availability",
    "author contribution",
)


def _is_reviewable_section(section: SectionInfo) -> bool:
    """Whether a parsed section is worth spending an agent call on.

    Judged on a section's text, not on its title. A marker-looking title is
    not evidence that the body is debris: when a page break falls immediately
    before a heading, the heading parser titles the section
    ``<!-- PAGE BREAK -->`` and the real heading stays in the body. On the
    benchmark paper one such section is 1,107 characters of "A.6 Proof of
    Theorem 2", the proof of the paper's central result. Filtering those by
    title discarded it.
    """
    if section.section_type == SectionType.REFERENCES:
        return False
    title = section.title.strip().lower().lstrip("#").strip()
    # Only treat a prefix match as boilerplate when the heading is short enough
    # to BE that boilerplate. "Funding" is a front-matter section; "Funding and
    # acquisition dynamics in venture capital" is a paper's results section, and
    # a bare prefix test would discard it.
    if len(title) <= _MAX_BOILERPLATE_TITLE_CHARS and any(
        title.startswith(prefix) for prefix in _SKIP_TITLE_PREFIXES
    ):
        return False
    if section.section_type == SectionType.APPENDIX:
        return len(section.text) >= _MIN_APPENDIX_CHARS
    # Any section with text is eligible. Scarcity is resolved by the ranking
    # below, not by a length cut: a length cut that is high enough to exclude
    # parser debris also excludes brief but substantive subsections, and when
    # the cap does not bind a short section costs one call that correctly
    # returns no comments.
    return bool(section.text.strip())


def select_reviewable_sections(
    sections: list[SectionInfo],
    *,
    limit: int = MAX_REVIEWABLE_SECTIONS,
) -> list[SectionInfo]:
    """Choose which sections get a section agent, in document order.

    Selection used to be ``[:limit]`` over document order. On a paper with more
    parsed sections than the cap that silently discarded the tail, and because
    appendices come last the tail is exactly where proofs live: on a 41-section
    theory paper every appendix proof was dropped before any agent saw it,
    including a 14k-character proof of the paper's main proposition.

    So: drop what is not reviewable at all, and if the cap still binds, keep
    the sections most likely to carry a finding — ranked by length, with
    mathematical content weighted up — rather than whichever happen to come
    first. The returned list is restored to document order, since downstream
    stages number and cross-reference comments by position.
    """
    candidates = [s for s in sections if _is_reviewable_section(s)]
    if len(candidates) <= limit:
        return candidates

    def weight(section: SectionInfo) -> float:
        return len(section.text) * (_MATH_SECTION_WEIGHT if section.math_content else 1.0)

    ranked = sorted(enumerate(candidates), key=lambda pair: -weight(pair[1]))
    kept_indices = sorted(index for index, _ in ranked[:limit])
    dropped = [candidates[i].title for i in range(len(candidates)) if i not in set(kept_indices)]
    logger.info(
        "Section cap %d binds on %d reviewable sections; skipping: %s",
        limit,
        len(candidates),
        ", ".join(dropped) or "(none)",
    )
    return [candidates[i] for i in kept_indices]


# Minimum text length for proof_verify to run on a math-flagged section.
_MIN_PROOF_VERIFY_SECTION_CHARS = 500

# Soft ceiling on the final detailed-comment count. The editorial pass is a
# single LLM call with no built-in count cap, so on a comment-heavy paper it
# can return 60-80 lightly-deduped comments one run and ~18 the next for the
# same input (#200). 25 is generous versus the ~20-comment refine.ink
# reference, so it only bites pathological over-generation, not well-
# deduplicated output. See _cap_comments for the ordering caveat.
_MAX_FINAL_COMMENTS = 25


def _cap_comments(comments: list[DetailedComment]) -> list[DetailedComment]:
    """Truncate an over-long comment list to the leading ``_MAX_FINAL_COMMENTS`` (#200).

    On the editorial / crossref / critique success paths the list is already
    ordered by importance (those prompts order critical -> major -> minor), so
    the dropped tail is the lowest-value comments. On the rare double-failure
    fallback (editorial AND crossref both raised), the list is raw section
    order, so the cap there is purely a bounded-output safety net rather than a
    severity-aware trim.
    """
    if len(comments) > _MAX_FINAL_COMMENTS:
        logger.info(
            "Capping %d editorial comments to %d (severity-ordered tail dropped)",
            len(comments),
            _MAX_FINAL_COMMENTS,
        )
        return comments[:_MAX_FINAL_COMMENTS]
    return comments


def _section_needs_proof_verify(section: SectionInfo) -> bool:
    """Return True iff proof_verify should chain after the section agent."""
    if not section.math_content:
        return False
    if section.claims:
        return True
    return len(section.text) >= _MIN_PROOF_VERIFY_SECTION_CHARS


def _verify_with_fallback(
    comments: list[DetailedComment],
    paper_markdown: str,
    *,
    stage_name: str,
    drop_unverified: bool = False,
) -> list[DetailedComment]:
    """Run quote verification, keeping originals if everything is dropped."""
    verified = verify_quotes(comments, paper_markdown, drop_unverified=drop_unverified)
    if comments and not verified:
        logger.warning("%s dropped ALL comments — keeping original comments", stage_name)
        return comments
    return verified


def _detect_section_focus(section: SectionInfo) -> str:
    """Detect section focus from the section type and math-content flag."""
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
    paper_markdown: str,
    paper_title: str,
    overview: OverviewFeedback | None,
    calibration: DomainCalibration | None,
    focus: str,
    literature_context: str,
    all_sections: list[SectionInfo],
    abstract: str,
    *,
    document_form: DocumentForm = "manuscript",
    author_notes: str | None = None,
    language: str | None = None,
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
        author_notes=author_notes,
        language=language,
    )
    comments = _verify_with_fallback(
        comments,
        paper_markdown,
        stage_name=f"Section-agent quote verification for '{section.title}'",
    )
    if focus == "proof" and comments and _section_needs_proof_verify(section):
        comments = verify_agent.run(
            section,
            paper_title,
            comments,
            abstract=abstract,
            document_form=document_form,
            author_notes=author_notes,
            language=language,
        )
        comments = _verify_with_fallback(
            comments,
            paper_markdown,
            stage_name=f"Proof-verify quote verification for '{section.title}'",
        )
    return comments


def calibrate_domain(structure: PaperStructure, client: LLMClient) -> DomainCalibration | None:
    """Generate domain-specific review criteria from the paper's content."""
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
    """Extract the paper's stated contributions for downstream review stages."""
    intro_text = ""
    conclusion_text = ""
    for section in structure.sections:
        if section.section_type == SectionType.INTRODUCTION:
            intro_text = section.text
        elif section.section_type == SectionType.CONCLUSION:
            conclusion_text = section.text

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


def run_editorial_pass(
    client: LLMClient,
    paper_text: str,
    overview: OverviewFeedback,
    comments: list[DetailedComment],
    *,
    title: str = "",
    abstract: str = "",
    contribution_context: ContributionContext | None = None,
    document_form: DocumentForm = "manuscript",
    author_notes: str | None = None,
    language: str | None = None,
    editorial_agent_cls: type[EditorialAgent] | None = None,
    crossref_agent_cls: type[CrossrefAgent] | None = None,
    critique_agent_cls: type[CritiqueAgent] | None = None,
) -> list[DetailedComment]:
    """Run the primary editorial pass with the legacy fallback chain."""
    editorial_agent_cls = editorial_agent_cls or EditorialAgent
    crossref_agent_cls = crossref_agent_cls or CrossrefAgent
    critique_agent_cls = critique_agent_cls or CritiqueAgent

    editorial_agent = editorial_agent_cls(client)
    try:
        filtered_comments = editorial_agent.run(
            paper_text,
            overview,
            comments,
            title=title,
            abstract=abstract,
            contribution_context=contribution_context,
            document_form=document_form,
            author_notes=author_notes,
            language=language,
        )
        return _cap_comments(
            _verify_with_fallback(
                filtered_comments,
                paper_text,
                stage_name="Editorial quote verification",
            )
        )
    except Exception:
        logger.warning("Editorial agent failed, falling back to crossref+critique", exc_info=True)

    crossref_agent = crossref_agent_cls(client)
    critique_agent = critique_agent_cls(client)

    try:
        filtered_comments = crossref_agent.run(
            overview,
            comments,
            title=title,
            abstract=abstract,
            author_notes=author_notes,
        )
        filtered_comments = _verify_with_fallback(
            filtered_comments,
            paper_text,
            stage_name="Crossref quote verification",
        )
    except Exception:
        logger.warning("Crossref fallback also failed", exc_info=True)
        filtered_comments = comments

    try:
        filtered_comments = critique_agent.run(
            overview,
            filtered_comments,
            title=title,
            abstract=abstract,
            author_notes=author_notes,
        )
        return _cap_comments(
            _verify_with_fallback(
                filtered_comments,
                paper_text,
                stage_name="Critique quote verification",
            )
        )
    except Exception:
        logger.warning("Critique fallback also failed", exc_info=True)
        return _cap_comments(filtered_comments)


def _renumber_comments(comments: list[DetailedComment]) -> list[DetailedComment]:
    """Renumber comments sequentially 1..N."""
    return [c.model_copy(update={"number": i}) for i, c in enumerate(comments, start=1)]
