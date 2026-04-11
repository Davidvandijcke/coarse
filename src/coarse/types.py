from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PaperText(BaseModel):
    """Extracted PDF content as markdown with metadata."""

    full_markdown: str = Field(description="Full paper content as markdown")
    token_estimate: int = Field(
        description="Approximate token count of the full text",
    )
    garble_ratio: float = Field(
        default=0.0,
        description="Fraction of text detected as OCR garble (0.0-1.0)",
    )


class SectionType(str, Enum):
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    RELATED_WORK = "related_work"
    METHODOLOGY = "methodology"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    APPENDIX = "appendix"
    REFERENCES = "references"
    OTHER = "other"


class SectionInfo(BaseModel):
    """A single section of the paper with classified type and extracted content."""

    number: int | float | str = Field(
        description="Section number (e.g. 1, 2.1, 'A')",
    )
    title: str = Field(description="Section heading text")
    text: str = Field(description="Full text content of the section")
    section_type: SectionType = Field(
        default=SectionType.OTHER,
        description="Classified section type",
    )
    page_start: int = Field(
        default=0,
        description="Starting page number (0 if unknown)",
    )
    page_end: int = Field(
        default=0,
        description="Ending page number (0 if unknown)",
    )
    claims: list[str] = Field(
        default_factory=list,
        description="Key claims made in this section",
    )
    definitions: list[str] = Field(
        default_factory=list,
        description="Formal definitions introduced",
    )
    math_content: bool = Field(
        default=False,
        description=(
            "Whether section contains mathematical proofs, "
            "derivations, or formal definitions needing verification"
        ),
    )

    @field_validator("section_type", mode="before")
    @classmethod
    def _coerce_section_type(cls, v: str) -> str:
        """Map unknown section_type values to 'other'."""
        try:
            SectionType(v)
            return v
        except ValueError:
            return SectionType.OTHER.value


class PaperStructure(BaseModel):
    """Parsed paper structure with metadata and ordered sections."""

    title: str = Field(description="Paper title")
    domain: str = Field(
        description="Academic domain (e.g. 'social_sciences/economics')",
    )
    taxonomy: str = Field(
        description="Document type (e.g. 'academic/research_paper')",
    )
    abstract: str = Field(description="Paper abstract text")
    sections: list[SectionInfo] = Field(
        description="Ordered list of paper sections",
    )


class PaperMetadata(BaseModel):
    """Response model for cheap text-LLM metadata extraction."""

    title: str = Field(description="Exact paper title as it appears on the first page")
    domain: str
    taxonomy: str


class ContributionContext(BaseModel):
    """Paper's stated contribution extracted for downstream constraint injection."""

    main_claims: list[str] = Field(
        min_length=1,
        description="Paper's stated contributions (verbatim or close paraphrase)",
    )
    key_objects: list[str] = Field(
        default_factory=list,
        description="Key mathematical objects/quantities and what the paper claims about them",
    )
    stated_limitations: list[str] = Field(
        default_factory=list,
        description="Limitations the authors explicitly acknowledge",
    )
    author_defenses: list[str] = Field(
        default_factory=list,
        description="Anticipated objections the authors address (remarks, footnotes, appendices)",
    )
    methodology_type: str = Field(
        default="",
        description="Brief description of the paper's methodological approach",
    )


class OverviewIssue(BaseModel):
    """A single macro-level issue identified in the paper."""

    title: str = Field(description="Short title summarizing the issue")
    body: str = Field(description="Detailed explanation of the issue")


class OverviewFeedback(BaseModel):
    """Macro-level feedback containing high-level issues."""

    summary: str = Field(
        default="",
        description="Optional summary paragraph",
    )
    assessment: str = Field(
        default="",
        description=(
            "2-3 sentence assessment of the paper's contribution, "
            "significance, and what it does well"
        ),
    )
    issues: list[OverviewIssue] = Field(
        min_length=1,
        description="Macro-level issues",
    )
    recommendation: str = Field(
        default="",
        description=(
            "Editorial recommendation: one of 'accept', 'minor revision', "
            "'major revision', or 'reject', with 2-3 sentence justification"
        ),
    )
    revision_targets: list[str] = Field(
        default_factory=list,
        description=(
            "If recommendation is not 'accept': 2-5 specific things a "
            "revision must accomplish, ordered by importance"
        ),
    )


class DetailedComment(BaseModel):
    """A single detailed review comment with verbatim quote and feedback."""

    number: int = Field(description="Sequential comment number")
    title: str = Field(
        description="Short title summarizing the comment",
    )
    quote: str = Field(
        min_length=20,
        description="Verbatim quote from the paper (min 20 chars)",
    )
    feedback: str = Field(
        description="Constructive feedback with remediation guidance",
    )
    status: Literal["Pending"] = Field(
        default="Pending",
        description="Review status",
    )
    severity: Literal["critical", "major", "minor"] = Field(
        default="major",
        description="Issue severity level",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="Reviewer confidence",
    )


class Review(BaseModel):
    """Complete paper review with overall feedback and detailed comments."""

    title: str = Field(description="Paper title")
    domain: str = Field(description="Academic domain")
    taxonomy: str = Field(description="Document type")
    date: str = Field(description="Review date (MM/DD/YYYY)")
    overall_feedback: OverviewFeedback = Field(
        description="Macro-level feedback (4-8 issues)",
    )
    detailed_comments: list[DetailedComment] = Field(
        description="Detailed review comments (8-18)",
    )


class DomainCalibration(BaseModel):
    """Domain-specific review criteria generated dynamically from paper content."""

    methodology_concerns: list[str] = Field(
        description="3-5 key methodological concerns for this type of paper"
    )
    assumption_red_flags: list[str] = Field(
        description="Assumptions that commonly fail in this domain"
    )
    what_not_to_check: list[str] = Field(description="What is irrelevant for this paper type")
    evaluation_standards: list[str] = Field(
        description="What a top-tier journal in this field expects"
    )


class MathSectionDetection(BaseModel):
    """Response model for LLM-based math section detection."""

    math_section_indices: list[int] = Field(
        default_factory=list,
        description=(
            "Indices (0-based) of sections containing mathematical content needing verification"
        ),
    )


class ExtractionError(Exception):
    """Raised when PDF text extraction produces unusable output."""


class CostStage(BaseModel):
    """Cost breakdown for a single pipeline stage."""

    name: str = Field(
        description="Pipeline stage name (e.g. 'structure', 'overview')",
    )
    model: str = Field(description="LLM model ID used for this stage")
    estimated_tokens_in: int = Field(
        description="Estimated input tokens",
    )
    estimated_tokens_out: int = Field(
        description="Estimated output tokens",
    )
    estimated_cost_usd: float = Field(
        description="Estimated cost in USD",
    )


class CostEstimate(BaseModel):
    """Pre-flight cost estimate for the full review pipeline."""

    stages: list[CostStage] = Field(
        description="Breakdown by pipeline stage",
    )
    total_cost_usd: float = Field(
        description="Total estimated cost in USD",
    )
