"""Synthesis — converts a Review object to refine.ink-format markdown.

Date field is emitted as-is from Review.date (no reformatting) to preserve fidelity.
"""
from __future__ import annotations

from coarse.types import Review


def render_review(review: Review) -> str:
    """Convert a Review to a refine.ink-format markdown string.

    Pure deterministic function; makes no LLM calls.
    """
    parts: list[str] = []

    # --- Header block ---
    parts.append(f"# {review.title}\n")
    parts.append(f"**Date**: {review.date}")
    parts.append(f"**Domain**: {review.domain}")
    parts.append(f"**Taxonomy**: {review.taxonomy}")
    parts.append("**Filter**: Active comments\n")
    parts.append("---\n")

    # --- Overall Feedback ---
    parts.append("## Overall Feedback\n")
    parts.append("Here are some overall reactions to the document.\n")

    for issue in review.overall_feedback.issues:
        parts.append(f"**{issue.title}**\n")
        parts.append(f"{issue.body}\n")

    parts.append("**Status**: [Pending]\n")
    parts.append("---\n")

    # --- Detailed Comments (grouped by severity) ---
    n = len(review.detailed_comments)
    parts.append(f"## Detailed Comments ({n})\n")

    # Group by severity: critical first, then major, then minor
    severity_order = {"critical": 0, "major": 1, "minor": 2}
    sorted_comments = sorted(
        review.detailed_comments,
        key=lambda c: severity_order.get(c.severity, 1),
    )

    for comment in sorted_comments:
        severity_label = f" [{comment.severity.upper()}]" if comment.severity != "major" else ""
        parts.append(f"### {comment.number}. {comment.title}{severity_label}\n")
        parts.append("**Status**: [Pending]\n")
        # Prefix every line of the quote with "> " for multi-line block-quotes
        quoted_lines = "\n> ".join(comment.quote.splitlines())
        parts.append(f"**Quote**:\n> {quoted_lines}\n")
        parts.append(f"**Feedback**:\n{comment.feedback}\n")
        parts.append("---\n")

    return "\n".join(parts)
