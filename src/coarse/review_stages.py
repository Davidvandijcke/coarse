"""Stage-local review helpers used by the pipeline orchestrator."""

from __future__ import annotations

import logging

from coarse.agents.critique import CritiqueAgent
from coarse.agents.crossref import CrossrefAgent
from coarse.agents.editorial import EditorialAgent
from coarse.agents.section import SectionAgent
from coarse.agents.verify import ProofVerifyAgent
from coarse.llm import LLMClient
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

# Minimum text length for proof_verify to run on a math-flagged section.
_MIN_PROOF_VERIFY_SECTION_CHARS = 500


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
        )
        return _verify_with_fallback(
            filtered_comments,
            paper_text,
            stage_name="Editorial quote verification",
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
        return _verify_with_fallback(
            filtered_comments,
            paper_text,
            stage_name="Critique quote verification",
        )
    except Exception:
        logger.warning("Critique fallback also failed", exc_info=True)
        return filtered_comments
