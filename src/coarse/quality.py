"""Quality evaluation for coarse reviews (dev-only module).

Compares a generated review against a reference review using an LLM judge.
Supports both single-judge and multi-judge panel evaluation with synthesis.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel

from coarse.llm import LLMClient
from coarse.synthesis import render_review
from coarse.types import Review

logger = logging.getLogger(__name__)


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


# ---------------------------------------------------------------------------
# Multi-judge panel evaluation with synthesizer
# ---------------------------------------------------------------------------

# Each judge gets a distinct persona to encourage diverse perspectives.
_JUDGE_PERSONAS = [
    "You are an expert in mathematical methodology and statistical theory. "
    "Focus especially on proof correctness, rate conditions, and whether "
    "assumptions are internally consistent.",
    "You are an expert in empirical research design and applied methodology. "
    "Focus especially on whether the paper's empirical implementation matches "
    "its theoretical claims, and whether simulations test the right properties.",
    "You are an expert in scientific communication and research impact. "
    "Focus especially on whether the review identifies the most important "
    "issues, whether comments are actionable, and whether coverage is complete.",
]


def _make_panel_system(persona: str) -> str:
    """Build judge system prompt with a specific persona prefix."""
    return persona + "\n\n" + _JUDGE_SYSTEM


class _SynthesisOutput(BaseModel):
    dimensions: list[DimensionScore]
    strengths: list[str]
    weaknesses: list[str]
    improvement_suggestions: list[str]


_SYNTHESIS_SYSTEM = """\
You are a meta-evaluator synthesizing multiple independent quality assessments \
of an AI-generated academic paper review. You have received reports from a panel \
of expert judges, each with a distinct perspective (methodology, empirical design, \
communication).

Your task:
1. For each dimension (coverage, specificity, depth, format), determine a final \
consensus score (1-5) that reflects the panel's assessments. Weight disagreements \
toward the more critical judge — overrating quality is worse than underrating it.
2. Synthesize 3-5 key strengths from across all judges' reports (deduplicate).
3. Synthesize 3-5 key weaknesses (deduplicate and prioritize the most actionable).
4. Provide 3-5 concrete improvement_suggestions for the review pipeline — \
specific, actionable changes that would address the weaknesses identified. \
Focus on what the *system* should do differently, not what the paper author \
should fix.

For each dimension score, provide reasoning that references which judges agreed \
or disagreed and why you chose the final score.
"""


def _synthesis_user(reports: list[QualityReport]) -> str:
    """Build user prompt for the synthesizer from multiple judge reports."""
    parts = []
    for i, report in enumerate(reports):
        label = ["Methodology Judge", "Empirical Judge", "Communication Judge"][i]
        dims = "\n".join(
            f"  - {d.dimension}: {d.score}/5 — {d.reasoning}"
            for d in report.dimensions
        )
        strengths = "\n".join(f"  + {s}" for s in report.strengths)
        weaknesses = "\n".join(f"  - {w}" for w in report.weaknesses)
        parts.append(
            f"### {label} (Overall: {report.overall_score:.1f})\n"
            f"**Scores:**\n{dims}\n"
            f"**Strengths:**\n{strengths}\n"
            f"**Weaknesses:**\n{weaknesses}"
        )

    return f"""\
Synthesize the following quality assessments from a panel of 3 expert judges.

{chr(10).join(parts)}

Determine consensus scores, synthesize strengths/weaknesses, and provide \
concrete improvement suggestions for the review generation pipeline.
"""


def evaluate_review_panel(
    generated: str | Review,
    reference: str,
    client: LLMClient | None = None,
    paper_text: str = "",
) -> tuple[QualityReport, list[QualityReport]]:
    """Multi-judge panel evaluation with synthesis.

    Runs 3 judges in parallel (each with a different expert persona),
    then synthesizes their reports into a final consensus.

    Returns:
        (synthesized_report, individual_reports)
    """
    if client is None:
        client = LLMClient()

    if isinstance(generated, Review):
        generated = render_review(generated)

    user_content = _judge_user(reference, generated, paper_text)

    def _run_judge(persona: str) -> QualityReport:
        messages = [
            {"role": "system", "content": _make_panel_system(persona)},
            {"role": "user", "content": user_content},
        ]
        result: _JudgeOutput = client.complete(
            messages, _JudgeOutput, max_tokens=4096
        )
        overall = sum(d.score for d in result.dimensions) / len(result.dimensions)
        return QualityReport(
            overall_score=overall,
            dimensions=result.dimensions,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
        )

    # Run judges in parallel
    individual_reports: list[QualityReport] = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_run_judge, p) for p in _JUDGE_PERSONAS]
        for i, future in enumerate(futures):
            try:
                individual_reports.append(future.result())
            except Exception:
                logger.warning("Judge %d failed, skipping", i)

    if not individual_reports:
        raise RuntimeError("All judges failed")

    # If only 1-2 judges succeeded, skip synthesis and average directly
    if len(individual_reports) < 3:
        return _average_reports(individual_reports), individual_reports

    # Synthesize
    synth_messages = [
        {"role": "system", "content": _SYNTHESIS_SYSTEM},
        {"role": "user", "content": _synthesis_user(individual_reports)},
    ]
    synth: _SynthesisOutput = client.complete(
        synth_messages, _SynthesisOutput, max_tokens=4096
    )
    overall = sum(d.score for d in synth.dimensions) / len(synth.dimensions)
    synthesized = QualityReport(
        overall_score=overall,
        dimensions=synth.dimensions,
        strengths=synth.strengths,
        weaknesses=synth.weaknesses,
    )
    return synthesized, individual_reports


def _average_reports(reports: list[QualityReport]) -> QualityReport:
    """Simple average fallback when synthesis isn't possible."""
    dim_scores: dict[str, list[int]] = {}
    for r in reports:
        for d in r.dimensions:
            dim_scores.setdefault(d.dimension, []).append(d.score)

    dims = [
        DimensionScore(
            dimension=name,
            score=round(sum(scores) / len(scores)),
            reasoning=f"Average of {len(scores)} judge(s)",
        )
        for name, scores in dim_scores.items()
    ]
    overall = sum(d.score for d in dims) / len(dims) if dims else 0.0
    all_strengths = [s for r in reports for s in r.strengths]
    all_weaknesses = [w for r in reports for w in r.weaknesses]
    return QualityReport(
        overall_score=overall,
        dimensions=dims,
        strengths=all_strengths[:5],
        weaknesses=all_weaknesses[:5],
    )
