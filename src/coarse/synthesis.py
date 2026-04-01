"""Synthesis — converts a Review object to structured review markdown.

Date field is emitted as-is from Review.date (no reformatting) to preserve fidelity.
"""
from __future__ import annotations

import re

from coarse.types import Review

# HTML tags that could execute code or load external resources
_DANGEROUS_HTML_RE = re.compile(
    r"<\s*/?\s*(?:script|iframe|object|embed|style|link|form|input|button|textarea"
    r"|select|meta|base|applet|svg|math)\b[^>]*>",
    re.IGNORECASE,
)
# Event handler attributes (onclick, onerror, onload, etc.)
_EVENT_HANDLER_RE = re.compile(r"\bon\w+\s*=", re.IGNORECASE)


def _sanitize_html(text: str) -> str:
    """Strip dangerous HTML tags and event handler attributes from text.

    Prevents XSS if the output markdown is rendered in a web context.
    Preserves benign markdown formatting.
    """
    text = _DANGEROUS_HTML_RE.sub("", text)
    text = _EVENT_HANDLER_RE.sub("", text)
    return text


def render_review(review: Review) -> str:
    """Convert a Review to a structured review markdown string.

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

    if review.overall_feedback.summary:
        parts.append("**Outline**\n")
        parts.append(f"{_sanitize_html(review.overall_feedback.summary)}\n")

    if review.overall_feedback.assessment:
        parts.append(f"{_sanitize_html(review.overall_feedback.assessment)}\n")

    for issue in review.overall_feedback.issues:
        parts.append(f"**{_sanitize_html(issue.title)}**\n")
        parts.append(f"{_sanitize_html(issue.body)}\n")

    parts.append("**Status**: [Pending]\n")
    parts.append("---\n")

    # --- Detailed Comments (pipeline order) ---
    n = len(review.detailed_comments)
    parts.append(f"## Detailed Comments ({n})\n")

    for comment in review.detailed_comments:
        title = _sanitize_html(comment.title)
        quote = _sanitize_html(comment.quote)
        feedback = _sanitize_html(comment.feedback)
        parts.append(f"### {comment.number}. {title}\n")
        parts.append("**Status**: [Pending]\n")
        # Prefix every line of the quote with "> " for multi-line block-quotes
        quoted_lines = "\n> ".join(quote.splitlines())
        parts.append(f"**Quote**:\n> {quoted_lines}\n")
        parts.append(f"**Feedback**:\n{feedback}\n")
        parts.append("---\n")

    return "\n".join(parts)
