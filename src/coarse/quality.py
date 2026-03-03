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
You are an expert academic peer review evaluator. You have access to the \
original paper, a high-quality reference review, and a generated review. \
Your task is to assess the generated review's quality both independently \
and relative to the reference.

Score each dimension from 1 (very poor) to 5 (excellent):

1. **coverage**: Does the generated review identify the paper's most important \
issues? Use the reference review as a guide for what matters, but also credit \
the generated review for finding valid issues the reference missed. Score 5 if \
all major issues are covered, 1 if most are missing.
2. **specificity**: Are comments precise, with correct verbatim quotes from the \
paper and actionable guidance? Verify quotes against the paper text. Score 5 if \
every comment has an accurate quote and clear fix, 1 if comments are vague or \
quotes are fabricated.
3. **depth**: Is the analysis substantive and technically rigorous? Does it \
engage with the paper's methodology, proofs, and assumptions at a deep level, \
or does it stay surface-level (notation complaints, formatting issues)? Score 5 \
for deep methodological insight, 1 for shallow observations.
4. **format**: Does the generated review adhere to the refine.ink structure \
(header block, Overall Feedback with titled issues, Detailed Comments with \
numbered entries, each with Quote and Feedback sections)? Score 5 for perfect \
adherence, 1 for major structural deviation.

For each dimension, provide a brief reasoning string (1-2 sentences).

Also provide 2-3 strengths and 2-3 weaknesses of the generated review as brief \
bullet strings.

Do not compute overall_score — it will be computed externally.
"""


def _judge_user(reference: str, generated: str, paper_text: str = "") -> str:
    paper_block = ""
    if paper_text:
        # Truncate to ~80k chars to stay within context limits
        if len(paper_text) > 80_000:
            paper_text = paper_text[:80_000] + "\n\n[...truncated]"
        paper_block = f"""
## Original Paper
<paper>
{paper_text}
</paper>

"""
    return f"""\
Evaluate the following generated review against the reference review.
{paper_block}
## Reference Review
<reference>
{reference}
</reference>

## Generated Review
<generated>
{generated}
</generated>

Score the generated review on: coverage, specificity, depth, and format (each 1-5).
Verify quotes against the paper text. Assess depth independently — does the \
generated review engage with the paper's actual methodology and assumptions?
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
    paper_text: str = "",
) -> QualityReport:
    """LLM-judge evaluation of a generated review against a reference.

    Accepts Review object or rendered markdown string.
    If paper_text is provided, the judge can verify quotes and
    independently assess coverage and depth.
    Returns structured quality report.
    Creates a default LLMClient if none provided.
    """
    if client is None:
        client = LLMClient()

    if isinstance(generated, Review):
        generated = render_review(generated)

    messages = [
        {"role": "system", "content": _JUDGE_SYSTEM},
        {"role": "user", "content": _judge_user(reference, generated, paper_text)},
    ]

    result: _JudgeOutput = client.complete(messages, _JudgeOutput, max_tokens=4096)

    overall_score = sum(d.score for d in result.dimensions) / len(result.dimensions)

    return QualityReport(
        overall_score=overall_score,
        dimensions=result.dimensions,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
    )
