"""Recall-based evaluation against ground-truth expert reviews.

Measures what percentage of expert-identified errors the system actually found.
Two-stage matching: location-based (cheap, via quote overlap) then semantic
(LLM judge for unmatched pairs).
"""
from __future__ import annotations

import datetime
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel, Field

from coarse.llm import LLMClient
from coarse.models import QUALITY_MODEL
from coarse.types import DetailedComment

logger = logging.getLogger(__name__)


class _YesNo(BaseModel):
    """Binary answer for semantic matching judge."""
    answer: str = Field(description="YES or NO")

# ---------------------------------------------------------------------------
# Ground-truth comment model
# ---------------------------------------------------------------------------


class GroundTruthComment(BaseModel):
    """A single comment parsed from a reference review."""

    index: int = Field(description="1-based comment index")
    title: str = Field(default="", description="Comment title if available")
    quote: str = Field(default="", description="Verbatim quote if available")
    feedback_text: str = Field(description="The comment's feedback/explanation")


# ---------------------------------------------------------------------------
# Parsers for different reference review formats
# ---------------------------------------------------------------------------

# Refine.ink format: ### N. Title / **Quote**: / **Feedback**:
_REFINE_COMMENT_RE = re.compile(
    r"###\s*(\d+)\.\s*(.+?)$",
    re.MULTILINE,
)

_QUOTE_BLOCK_RE = re.compile(
    r"\*\*Quote\*\*:\s*\n>\s*(.+?)(?=\n\n|\n\*\*)",
    re.DOTALL,
)

_FEEDBACK_BLOCK_RE = re.compile(
    r"\*\*Feedback\*\*:\s*\n(.+?)(?=\n---|\Z)",
    re.DOTALL,
)


def parse_refine_review(markdown: str) -> list[GroundTruthComment]:
    """Parse a refine.ink-format review into ground-truth comments.

    Expects: ### N. Title / **Quote**: > text / **Feedback**: text
    Also handles the coarse output format (identical structure).
    """
    comments: list[GroundTruthComment] = []

    # Split on comment headers
    headers = list(_REFINE_COMMENT_RE.finditer(markdown))
    for i, match in enumerate(headers):
        idx = int(match.group(1))
        title = match.group(2).strip()

        # Extract the block between this header and the next (or end)
        start = match.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(markdown)
        block = markdown[start:end]

        # Extract quote
        quote = ""
        q_match = _QUOTE_BLOCK_RE.search(block)
        if q_match:
            quote = q_match.group(1).strip()

        # Extract feedback
        feedback = ""
        f_match = _FEEDBACK_BLOCK_RE.search(block)
        if f_match:
            feedback = f_match.group(1).strip()

        # Fallback: use the whole block as feedback if no explicit sections
        if not feedback:
            feedback = block.strip()

        comments.append(GroundTruthComment(
            index=idx, title=title, quote=quote, feedback_text=feedback,
        ))

    return comments


# Numbered plain-text comments: "N. Text..."
_NUMBERED_RE = re.compile(r"(?:^|\n)(\d+)\.\s+", re.MULTILINE)


def parse_plain_review(markdown: str) -> list[GroundTruthComment]:
    """Parse a plain numbered-list review (Reviewer3, Stanford).

    Handles formats with:
    - Multiple reviewer sections (# Study Design Reviewer, etc.)
    - Numbered comments (1. Text...)
    """
    comments: list[GroundTruthComment] = []
    global_idx = 0

    # Find all numbered items
    matches = list(_NUMBERED_RE.finditer(markdown))
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        text = markdown[start:end].strip()

        # Skip very short items (likely not real comments)
        if len(text) < 50:
            continue

        global_idx += 1

        # Try to extract title from first sentence
        title = ""
        first_period = text.find(".")
        first_colon = text.find(":")
        sep = min(
            p for p in (first_period, first_colon) if p > 0
        ) if any(p > 0 for p in (first_period, first_colon)) else -1
        if 0 < sep < 120:
            title = text[:sep].strip()

        comments.append(GroundTruthComment(
            index=global_idx, title=title, quote="", feedback_text=text,
        ))

    return comments


def parse_review_auto(markdown: str) -> list[GroundTruthComment]:
    """Auto-detect format and parse a reference review."""
    # Refine.ink format has ### N. headers
    if _REFINE_COMMENT_RE.search(markdown):
        return parse_refine_review(markdown)
    return parse_plain_review(markdown)


# ---------------------------------------------------------------------------
# Matching functions
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase word set."""
    return set(re.findall(r"\w+", text.lower()))


def _jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity between two token sets."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def location_match(
    gt: GroundTruthComment,
    pred: DetailedComment,
    threshold: float = 0.25,
) -> bool:
    """Check if two comments match by quote/text overlap.

    Compares gt.quote vs pred.quote, and falls back to gt.feedback_text
    vs pred.feedback if quotes are unavailable.
    """
    # Primary: quote-to-quote match
    if gt.quote and pred.quote:
        sim = _jaccard(_tokenize(gt.quote), _tokenize(pred.quote))
        if sim >= threshold:
            return True

    # Secondary: quote-to-feedback cross-match
    gt_text = gt.quote or gt.feedback_text
    pred_text = pred.quote or pred.feedback

    sim = _jaccard(_tokenize(gt_text), _tokenize(pred_text))
    if sim >= threshold:
        return True

    # Tertiary: feedback-to-feedback (lower threshold for semantic overlap)
    fb_sim = _jaccard(_tokenize(gt.feedback_text), _tokenize(pred.feedback))
    return fb_sim >= threshold * 1.5


_SEMANTIC_JUDGE_SYSTEM = """\
You are evaluating whether two review comments identify the same issue in an \
academic paper. They do NOT need to use the same wording. They match if they \
point to the same underlying error or problem, even if described differently.

Answer with exactly one word: YES or NO.
"""


def _semantic_judge_prompt(gt: GroundTruthComment, pred: DetailedComment) -> str:
    gt_block = f"Title: {gt.title}\n" if gt.title else ""
    gt_block += f"Quote: {gt.quote}\n" if gt.quote else ""
    gt_block += f"Feedback: {gt.feedback_text[:500]}"

    pred_block = (
        f"Title: {pred.title}\n"
        f"Quote: {pred.quote}\n"
        f"Feedback: {pred.feedback[:500]}"
    )

    return f"""\
Do these two review comments identify the same issue in the paper?

## Comment A (expert reference)
{gt_block}

## Comment B (generated)
{pred_block}

Answer YES or NO.
"""


def semantic_match(
    gt: GroundTruthComment,
    pred: DetailedComment,
    client: LLMClient,
) -> bool:
    """Use a cheap LLM judge to determine if two comments address the same issue."""
    messages = [
        {"role": "system", "content": _SEMANTIC_JUDGE_SYSTEM},
        {"role": "user", "content": _semantic_judge_prompt(gt, pred)},
    ]
    try:
        result = client.complete(messages, _YesNo, max_tokens=16, temperature=0.0)
        return result.answer.strip().upper().startswith("YES")
    except Exception:
        logger.warning("Semantic match failed, defaulting to no match", exc_info=True)
        return False


# ---------------------------------------------------------------------------
# Recall computation
# ---------------------------------------------------------------------------


class MatchPair(BaseModel):
    """A matched pair of ground-truth and generated comments."""

    gt_index: int
    pred_number: int
    match_type: str = Field(description="'location' or 'semantic'")


class RecallReport(BaseModel):
    """Recall evaluation results."""

    location_recall: float = Field(description="Recall using location matching only")
    semantic_recall: float = Field(
        description="Recall using location + semantic matching",
    )
    precision: float = Field(description="Precision (semantic)")
    f1: float = Field(description="F1 score (semantic)")
    n_ground_truth: int
    n_generated: int
    matched_pairs: list[MatchPair]
    unmatched_gt: list[int] = Field(
        description="Indices of unmatched ground-truth comments",
    )
    unmatched_pred: list[int] = Field(
        description="Numbers of unmatched generated comments",
    )


def compute_recall(
    generated: list[DetailedComment] | str,
    reference: list[GroundTruthComment] | str,
    client: LLMClient | None = None,
    model: str = QUALITY_MODEL,
    location_threshold: float = 0.25,
) -> RecallReport:
    """Compute recall of generated review against ground-truth reference.

    If generated/reference are strings (markdown), parse them automatically.
    Location matching is always run. Semantic matching requires a client
    (or creates one using the provided model).
    """
    # Parse if needed
    if isinstance(generated, str):
        gen_comments = parse_refine_review(generated)
        generated = [
            DetailedComment(
                number=c.index, title=c.title,
                quote=c.quote or "placeholder quote text",
                feedback=c.feedback_text,
            )
            for c in gen_comments
        ]
    if isinstance(reference, str):
        reference = parse_review_auto(reference)

    if not reference:
        return RecallReport(
            location_recall=0.0, semantic_recall=0.0, precision=0.0, f1=0.0,
            n_ground_truth=0, n_generated=len(generated),
            matched_pairs=[], unmatched_gt=[], unmatched_pred=[],
        )

    # Phase 1: Location matching (free)
    matched_pairs: list[MatchPair] = []
    matched_gt: set[int] = set()
    matched_pred: set[int] = set()

    for gt in reference:
        for pred in generated:
            if pred.number in matched_pred:
                continue
            if location_match(gt, pred, threshold=location_threshold):
                matched_pairs.append(MatchPair(
                    gt_index=gt.index, pred_number=pred.number,
                    match_type="location",
                ))
                matched_gt.add(gt.index)
                matched_pred.add(pred.number)
                break

    location_recall = len(matched_gt) / len(reference)

    # Phase 2: Semantic matching for unmatched pairs (costs LLM calls)
    if client is None:
        client = LLMClient(model=model)

    unmatched_gt_comments = [g for g in reference if g.index not in matched_gt]
    unmatched_pred_comments = [p for p in generated if p.number not in matched_pred]

    if unmatched_gt_comments and unmatched_pred_comments:
        # Run semantic matching in parallel for speed
        def _check_pair(
            gt: GroundTruthComment, pred: DetailedComment,
        ) -> tuple[GroundTruthComment, DetailedComment, bool]:
            return gt, pred, semantic_match(gt, pred, client)

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = []
            for gt in unmatched_gt_comments:
                for pred in unmatched_pred_comments:
                    futures.append(pool.submit(_check_pair, gt, pred))

            # Greedy matching: first semantic match wins
            for future in futures:
                gt, pred, is_match = future.result()
                if is_match and gt.index not in matched_gt and pred.number not in matched_pred:
                    matched_pairs.append(MatchPair(
                        gt_index=gt.index, pred_number=pred.number,
                        match_type="semantic",
                    ))
                    matched_gt.add(gt.index)
                    matched_pred.add(pred.number)

    semantic_recall = len(matched_gt) / len(reference)
    precision = len(matched_pred) / len(generated) if generated else 0.0
    f1 = (
        2 * semantic_recall * precision / (semantic_recall + precision)
        if (semantic_recall + precision) > 0 else 0.0
    )

    return RecallReport(
        location_recall=location_recall,
        semantic_recall=semantic_recall,
        precision=precision,
        f1=f1,
        n_ground_truth=len(reference),
        n_generated=len(generated),
        matched_pairs=matched_pairs,
        unmatched_gt=[g.index for g in reference if g.index not in matched_gt],
        unmatched_pred=[p.number for p in generated if p.number not in matched_pred],
    )


# ---------------------------------------------------------------------------
# Report persistence
# ---------------------------------------------------------------------------


def save_recall_report(
    report: RecallReport,
    output_path: Path,
    reference_path: str,
    generated_path: str,
    model: str = QUALITY_MODEL,
) -> None:
    """Write a recall report as a markdown file."""
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")

    pairs = "\n".join(
        f"| GT #{p.gt_index} | Pred #{p.pred_number} | {p.match_type} |"
        for p in report.matched_pairs
    )
    unmatched_gt = ", ".join(str(i) for i in report.unmatched_gt) or "(none)"
    unmatched_pred = ", ".join(str(i) for i in report.unmatched_pred) or "(none)"

    content = f"""\
# Recall Evaluation

**Timestamp**: {timestamp}
**Reference**: {reference_path}
**Generated**: {generated_path}
**Judge Model**: {model}

## Scores

| Metric | Value |
|--------|-------|
| Location Recall | {report.location_recall:.1%} |
| Semantic Recall | {report.semantic_recall:.1%} |
| Precision | {report.precision:.1%} |
| F1 | {report.f1:.1%} |
| Ground Truth Comments | {report.n_ground_truth} |
| Generated Comments | {report.n_generated} |

## Matched Pairs

| Ground Truth | Generated | Match Type |
|-------------|-----------|------------|
{pairs}

## Unmatched

- **Ground truth not found**: {unmatched_gt}
- **Generated with no match**: {unmatched_pred}
"""
    output_path.write_text(content, encoding="utf-8")
