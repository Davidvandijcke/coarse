from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PageContent(BaseModel):
    page_num: int
    text: str
    image_b64: Optional[str] = None


class PaperText(BaseModel):
    full_markdown: str
    pages: list[PageContent]
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


class OverviewIssue(BaseModel):
    title: str
    body: str


class OverviewFeedback(BaseModel):
    issues: list[OverviewIssue] = Field(min_length=1, max_length=8)


class DetailedComment(BaseModel):
    number: int
    title: str
    quote: str
    feedback: str
    status: Literal["Pending"] = "Pending"


class Review(BaseModel):
    title: str
    domain: str
    taxonomy: str
    date: str
    overall_feedback: OverviewFeedback
    detailed_comments: list[DetailedComment]


class CostStage(BaseModel):
    name: str
    model: str
    estimated_tokens_in: int
    estimated_tokens_out: int
    estimated_cost_usd: float


class CostEstimate(BaseModel):
    stages: list[CostStage]
    total_cost_usd: float
