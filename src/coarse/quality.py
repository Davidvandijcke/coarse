"""Quality evaluation for coarse reviews (dev-only module).

Compares a generated review against a reference review using an LLM judge.
Supports both single-judge and multi-judge panel evaluation with synthesis.
"""
from __future__ import annotations

import base64
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from coarse.llm import LLMClient
from coarse.models import QUALITY_MODEL
from coarse.synthesis import render_review
from coarse.types import Review

logger = logging.getLogger(__name__)


class DimensionScore(BaseModel):
    dimension: str
    score: float  # 1.0-6.0 (5+ means exceeds reference quality)
    reasoning: str


class QualityReport(BaseModel):
    overall_score: float  # 1.0-6.0 (5+ means exceeds reference)
    dimensions: list[DimensionScore]
    strengths: list[str]
    weaknesses: list[str]


_JUDGE_SYSTEM = """\
You are an expert academic peer review evaluator. You have access to the \
original paper and two reviews labeled "Review A" and "Review B". One is a \
human-written reference and one is AI-generated. Your task is to assess \
Review B's quality primarily against the paper itself, using Review A \
for calibration.

IMPORTANT — Bias awareness:
- Do NOT favor a review because it is longer. A concise review that identifies \
real errors is better than a verbose review that pads with generic observations. \
Evaluate substance per comment, not total word count.
- Do NOT favor a review because it uses more confident or assertive language. \
A hedged but correct observation is better than a confident but wrong claim.
- Do NOT favor a review because it cites more sources or uses more technical \
jargon. Evaluate whether the technical content is correct, not whether it \
sounds impressive.
- USE THE FULL SCORING RANGE. A review with fabricated quotes or incorrect \
mathematical claims should score 1-2, not 3-4. Reserve scores of 3-4 for \
reviews that are mediocre but not actively wrong. Do not cluster scores in \
the middle of the scale.

Score each dimension from 1.0 to 6.0 in half-point increments \
(1, 1.5, 2, ..., 5, 5.5, 6). Use half-points to distinguish minor issues \
from major ones — e.g., one truncated quote out of 19 is a 4.5, not a 4.

The scale:
- 1.0-2.0: Major deficiencies — fabricated quotes, incorrect claims, \
missing the paper's central issues, or largely generic feedback
- 2.5-3.5: Partial quality — some valid points but significant gaps, \
errors in technical analysis, or mostly surface-level observations
- 4.0-4.5: Good but below reference — identifies real issues with \
some depth but misses important points or has minor inaccuracies
- 5.0: Matches the reference review in quality
- 5.5: Exceeds the reference — catches valid issues the reference missed, \
or provides deeper analysis on shared issues
- 6.0: Substantially exceeds the reference — identifies important errors or \
insights the reference missed entirely, with stronger evidence and reasoning

Award 5+ scores when Review B demonstrably surpasses Review A. \
This requires concrete evidence (e.g., found a real error the reference \
overlooked, provided a re-derivation where the reference only noted concern, \
or identified a cross-section inconsistency the reference missed).

Dimensions:
1. **coverage**: Does Review B identify the paper's most important \
issues? Evaluate this against the paper itself — what are the real strengths, \
weaknesses, and gaps? Review A may help calibrate what matters, but \
it is not the answer key. Credit Review B fully for finding valid \
issues Review A missed, and do not penalize it for omitting issues that \
are minor or debatable.
2. **specificity**: Are comments precise, with correct verbatim quotes from the \
paper and actionable guidance? Verify quotes against the paper text. Score 5 if \
every comment has an accurate quote and clear fix, 1 if comments are vague or \
quotes are fabricated. Score 5+ if quotes are more precise and fixes more \
concrete than Review A.
3. **depth**: Is the analysis substantive and technically rigorous? Does it \
engage with the paper's methodology, proofs, and assumptions at a deep level, \
or does it stay surface-level (notation complaints, formatting issues)? \
A long review full of surface observations scores LOWER than a short review \
with deep technical engagement. Score 5+ if the analysis provides deeper \
technical engagement than Review A \
(e.g., re-derivations, concrete counterexamples, numerical verification).

For each dimension, provide a brief reasoning string (1-2 sentences).

Also provide 2-3 strengths and 2-3 weaknesses of Review B as brief \
bullet strings.

Do not compute overall_score — it will be computed externally.
"""


def _judge_user(
    reference: str,
    generated: str,
    paper_text: str = "",
    paper_pdf: Path | None = None,
    swap: bool = False,
) -> str | list[dict]:
    """Build user prompt for judge.

    When swap=True, the generated review is presented as Review A
    and the reference as Review B (reversed). The judge always evaluates
    Review B. This is used for positional-bias mitigation.

    When paper_pdf is provided, returns multimodal content blocks (list[dict])
    with the PDF attached. Otherwise returns a plain string.
    paper_pdf takes priority over paper_text when both are provided.
    """
    if swap:
        review_a, review_b = generated, reference
    else:
        review_a, review_b = reference, generated

    # Build the paper reference note
    if paper_pdf is not None:
        paper_note = (
            "\n## Original Paper\n"
            "The paper is attached as a PDF. Use it as the primary source of "
            "truth for verifying quotes and assessing coverage.\n\n"
        )
    elif paper_text:
        paper_note = f"\n## Original Paper\n<paper>\n{paper_text}\n</paper>\n\n"
    else:
        paper_note = ""

    prompt_text = f"""\
Evaluate Review B below. Use the paper as the primary source of truth \
and Review A for calibration (Review A is not an answer key).
{paper_note}\
## Review A (for calibration)
<review_a>
{review_a}
</review_a>

## Review B (evaluate this)
<review_b>
{review_b}
</review_b>

Score Review B on: coverage, specificity, and depth \
(each 1.0-6.0 in half-point increments, where 5.0 = matches Review A, \
5.5-6.0 = exceeds Review A).
Verify quotes against the paper text. Assess coverage and depth against the \
paper itself — does Review B find the paper's real issues and \
engage with its actual methodology and assumptions? Credit valid issues \
Review A missed — if Review B catches real errors Review A \
overlooked, that warrants a score above 5.0. Provide reasoning for each score, \
plus 2-3 strengths and 2-3 weaknesses.
"""

    if paper_pdf is not None:
        pdf_b64 = base64.b64encode(paper_pdf.read_bytes()).decode()
        return [
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {
                "url": f"data:application/pdf;base64,{pdf_b64}",
            }},
        ]

    return prompt_text


class _JudgeOutput(BaseModel):
    dimensions: list[DimensionScore]
    strengths: list[str]
    weaknesses: list[str]


def evaluate_review(
    generated: str | Review,
    reference: str,
    client: LLMClient | None = None,
    paper_text: str = "",
    paper_pdf: Path | None = None,
    model: str = QUALITY_MODEL,
    max_tokens: int = 16384,
) -> QualityReport:
    """LLM-judge evaluation of a generated review against a reference.

    Mitigates positional bias by running the judge twice — once with the
    reference as Review A (normal) and once with the generated review as
    Review A (swapped) — then averaging dimension scores.

    Accepts Review object or rendered markdown string.
    If paper_pdf is provided, the PDF is sent as a multimodal attachment
    for quote verification (preferred). Falls back to paper_text if no PDF.
    Returns structured quality report.
    Creates a default LLMClient if none provided.
    """
    if client is None:
        client = LLMClient(model=model)

    if isinstance(generated, Review):
        generated = render_review(generated)

    def _run_judge(swap: bool) -> _JudgeOutput:
        messages = [
            {"role": "system", "content": _JUDGE_SYSTEM},
            {
                "role": "user",
                "content": _judge_user(
                    reference, generated, paper_text,
                    paper_pdf=paper_pdf, swap=swap,
                ),
            },
        ]
        return client.complete(messages, _JudgeOutput, max_tokens=max_tokens)

    # Run both orderings in parallel to mitigate positional bias
    with ThreadPoolExecutor(max_workers=2) as pool:
        fut_normal = pool.submit(_run_judge, False)
        fut_swapped = pool.submit(_run_judge, True)
        result_normal = fut_normal.result()
        result_swapped = fut_swapped.result()

    # When swapped, the judge scored the *reference* as Review B.
    # Invert those scores: if reference scored X, generated scores (10-X)
    # mapped back to 1-6 scale. Actually simpler: the swapped score
    # tells us how good the reference is relative to generated.
    # generated_quality ≈ 10 - swapped_reference_score doesn't work on
    # a 1-6 scale. Instead: swapped score S means "reference is S vs
    # generated". So generated vs reference ≈ mirror: 10 - S.
    # On a 1-6 scale with 5 as parity: deviation = S - 5, so
    # generated = 5 - deviation = 5 - (S - 5) = 10 - S.
    swapped_dims = {d.dimension: d for d in result_swapped.dimensions}

    averaged_dims = []
    for d in result_normal.dimensions:
        normal_score = d.score
        if d.dimension in swapped_dims:
            # Invert swapped score: if ref scored 5.5 vs gen, gen is 4.5
            inverted = 10.0 - swapped_dims[d.dimension].score
            # Clamp to valid range
            inverted = max(1.0, min(6.0, inverted))
            avg = round((normal_score + inverted) * 2) / 4  # nearest 0.25
            # Round to nearest 0.5 for final score
            avg = round(avg * 2) / 2
        else:
            avg = normal_score
        averaged_dims.append(DimensionScore(
            dimension=d.dimension,
            score=avg,
            reasoning=d.reasoning,
        ))

    overall = sum(d.score for d in averaged_dims) / len(averaged_dims)

    return QualityReport(
        overall_score=overall,
        dimensions=averaged_dims,
        strengths=result_normal.strengths,
        weaknesses=result_normal.weaknesses,
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
1. For each dimension (coverage, specificity, depth), determine a final \
consensus score (1.0-6.0 in half-point increments, where 5+ means exceeds \
the reference) that FAITHFULLY reflects the panel's actual scores. Your score \
must stay within the range of the judges' scores. Do NOT introduce your own \
independent assessment or dock points for issues the judges did not penalize. \
When judges disagree, weight toward the more critical judge.
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
            f"  - {d.dimension}: {d.score}/6 — {d.reasoning}"
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
    paper_pdf: Path | None = None,
    model: str = QUALITY_MODEL,
) -> tuple[QualityReport, list[QualityReport]]:
    """Multi-judge panel evaluation with synthesis.

    Runs 3 judges in parallel (each with a different expert persona),
    then synthesizes their reports into a final consensus.

    Returns:
        (synthesized_report, individual_reports)
    """
    if client is None:
        client = LLMClient(model=model)

    if isinstance(generated, Review):
        generated = render_review(generated)

    user_content = _judge_user(reference, generated, paper_text, paper_pdf=paper_pdf)

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
                logger.warning("Judge %d failed, skipping", i, exc_info=True)

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


def save_quality_report(
    report: QualityReport,
    output_path: Path,
    reference_path: str,
    model: str = QUALITY_MODEL,
    mode: str = "single",
) -> None:
    """Write a quality report as a markdown file.

    Includes timestamp, reference review path, model, and mode so results
    are reproducible and traceable across dev runs.
    """
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    dim_rows = "\n".join(
        f"| {d.dimension} | {d.score}/6 | {d.reasoning} |"
        for d in report.dimensions
    )
    strengths = "\n".join(f"- {s}" for s in report.strengths)
    weaknesses = "\n".join(f"- {w}" for w in report.weaknesses)

    content = f"""\
# Quality Evaluation

**Timestamp**: {timestamp}
**Reference**: {reference_path}
**Model**: {model}
**Mode**: {mode}

## Overall Score: {report.overall_score:.2f}/6.0

## Dimensions

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
{dim_rows}

## Strengths

{strengths}

## Weaknesses

{weaknesses}
"""
    output_path.write_text(content, encoding="utf-8")


def _average_reports(reports: list[QualityReport]) -> QualityReport:
    """Simple average fallback when synthesis isn't possible."""
    dim_scores: dict[str, list[float]] = {}
    for r in reports:
        for d in r.dimensions:
            dim_scores.setdefault(d.dimension, []).append(d.score)

    dims = [
        DimensionScore(
            dimension=name,
            score=round(sum(scores) / len(scores) * 2) / 2,  # nearest 0.5
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
