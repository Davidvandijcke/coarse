from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PaperText(BaseModel):
    full_markdown: str
    token_estimate: int


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
    number: int | float | str
    title: str
    text: str
    section_type: SectionType = SectionType.OTHER
    page_start: int = 0
    page_end: int = 0
    claims: list[str] = Field(default_factory=list)
    definitions: list[str] = Field(default_factory=list)

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
    title: str
    domain: str
    taxonomy: str
    abstract: str
    sections: list[SectionInfo]


class PaperMetadata(BaseModel):
    """Response model for cheap text-LLM domain/taxonomy classification."""
    domain: str
    taxonomy: str


class OverviewIssue(BaseModel):
    title: str
    body: str


class OverviewFeedback(BaseModel):
    summary: str = ""
    issues: list[OverviewIssue] = Field(min_length=1, max_length=8)


class DetailedComment(BaseModel):
    number: int
    title: str
    quote: str
    feedback: str
    status: Literal["Pending"] = "Pending"
    severity: Literal["critical", "major", "minor"] = "major"


class Review(BaseModel):
    title: str
    domain: str
    taxonomy: str
    date: str
    overall_feedback: OverviewFeedback
    detailed_comments: list[DetailedComment]


class DomainCalibration(BaseModel):
    """Domain-specific review criteria generated dynamically from paper content."""
    methodology_concerns: list[str] = Field(
        description="3-5 key methodological concerns for this type of paper"
    )
    assumption_red_flags: list[str] = Field(
        description="Assumptions that commonly fail in this domain"
    )
    what_not_to_check: list[str] = Field(
        description="What is irrelevant for this paper type"
    )
    evaluation_standards: list[str] = Field(
        description="What a top-tier journal in this field expects"
    )


class ExtractionError(Exception):
    """Raised when PDF text extraction produces unusable output."""


class CostStage(BaseModel):
    name: str
    model: str
    estimated_tokens_in: int
    estimated_tokens_out: int
    estimated_cost_usd: float


class CostEstimate(BaseModel):
    stages: list[CostStage]
    total_cost_usd: float
