"""Quality evaluation for coarse reviews (dev-only module).

Compares a generated review against a reference review using an LLM judge.
"""
from __future__ import annotations

from pydantic import BaseModel

from coarse.llm import LLMClient
from coarse.synthesis import render_review
from coarse.types import Review


class DimensionScore(BaseModel):
    dimension: str
    score: int  # 1-5
    reasoning: str


class QualityReport(BaseModel):
    overall_score: float  # 1.0-5.0, weighted average
    dimensions: list[DimensionScore]
    strengths: list[str]
    weaknesses: list[str]


_JUDGE_SYSTEM = """\
You are an expert academic peer review evaluator. Your task is to compare a \
generated paper review against a high-quality reference review and assess the \
generated review on four dimensions.

Score each dimension from 1 (very poor) to 5 (excellent):

1. **coverage**: Does the generated review identify the same major issues as the \
reference? Score 5 if all key issues are covered, 1 if most major issues are missing.
2. **specificity**: Are comments precise, with concrete quotes and actionable \
guidance? Score 5 if every comment has a verbatim quote and clear fix, 1 if \
comments are vague or generic.
3. **depth**: Is the analysis substantive and technically rigorous vs \
surface-level? Score 5 for deep methodological insight, 1 for shallow observations.
4. **format**: Does the generated review adhere to the refine.ink structure \
(header block, Overall Feedback with titled issues, Detailed Comments with \
numbered entries, each with Quote and Feedback sections)? Score 5 for perfect \
adherence, 1 for major structural deviation.

For each dimension, provide a brief reasoning string (1-2 sentences).

Also provide 2-3 strengths and 2-3 weaknesses of the generated review as brief \
bullet strings.

Do not compute overall_score — it will be computed externally.
"""


def _judge_user(reference: str, generated: str) -> str:
    return f"""\
Evaluate the following generated review against the reference review.

## Reference Review
<reference>
{reference}
</reference>

## Generated Review
<generated>
{generated}
</generated>

Score the generated review on: coverage, specificity, depth, and format (each 1-5).
Provide reasoning for each score, plus 2-3 strengths and 2-3 weaknesses.
"""


class _JudgeOutput(BaseModel):
    dimensions: list[DimensionScore]
    strengths: list[str]
    weaknesses: list[str]


def evaluate_review(
    generated: str | Review,
    reference: str,
    client: LLMClient | None = None,
) -> QualityReport:
    """LLM-judge evaluation of a generated review against a reference.

    Accepts Review object or rendered markdown string.
    Returns structured quality report.
    Creates a default LLMClient if none provided.
    """
    if client is None:
        client = LLMClient()

    if isinstance(generated, Review):
        generated = render_review(generated)

    messages = [
        {"role": "system", "content": _JUDGE_SYSTEM},
        {"role": "user", "content": _judge_user(reference, generated)},
    ]

    result: _JudgeOutput = client.complete(messages, _JudgeOutput)

    overall_score = sum(d.score for d in result.dimensions) / len(result.dimensions)

    return QualityReport(
        overall_score=overall_score,
        dimensions=result.dimensions,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
    )
