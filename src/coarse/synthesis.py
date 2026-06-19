"""Synthesis — converts a Review object to structured review markdown.

Date field is emitted as-is from Review.date (no reformatting) to preserve fidelity.
"""
from __future__ import annotations

import re

from coarse.review_labels import review_labels
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
    lang_code = review.language.review_language if review.language else ""
    L = review_labels(lang_code)

    parts: list[str] = []

    # --- Header block ---
    parts.append(f"# {review.title}\n")
    parts.append(f"**{L['date']}**: {review.date}")
    parts.append(f"**{L['domain']}**: {review.domain}")
    parts.append(f"**{L['taxonomy']}**: {review.taxonomy}")
    parts.append(f"**{L['filter']}**: {L['active_comments']}\n")
    parts.append("---\n")

    # --- Overall Feedback ---
    parts.append(f"## {L['overall_feedback']}\n")
    parts.append(f"{L['overall_intro']}\n")

    if review.overall_feedback.summary:
        parts.append(f"**{L['outline']}**\n")
        parts.append(f"{_sanitize_html(review.overall_feedback.summary)}\n")

    if review.overall_feedback.assessment:
        parts.append(f"{_sanitize_html(review.overall_feedback.assessment)}\n")

    for issue in review.overall_feedback.issues:
        parts.append(f"**{_sanitize_html(issue.title)}**\n")
        parts.append(f"{_sanitize_html(issue.body)}\n")

    if review.overall_feedback.recommendation:
        rec = _sanitize_html(review.overall_feedback.recommendation)
        parts.append(f"**{L['recommendation']}**: {rec}\n")

    if review.overall_feedback.revision_targets:
        parts.append(f"**{L['revision_targets']}**:\n")
        for i, target in enumerate(review.overall_feedback.revision_targets, 1):
            parts.append(f"{i}. {_sanitize_html(target)}")
        parts.append("")  # blank line

    parts.append(f"**{L['status']}**: [{L['pending']}]\n")
    parts.append("---\n")

    # --- Detailed Comments (pipeline order) ---
    n = len(review.detailed_comments)
    parts.append(f"## {L['detailed_comments']} ({n})\n")

    for comment in review.detailed_comments:
        title = _sanitize_html(comment.title)
        quote = _sanitize_html(comment.quote)
        feedback = _sanitize_html(comment.feedback)
        parts.append(f"### {comment.number}. {title}\n")
        parts.append(f"**{L['status']}**: [{L['pending']}]\n")
        # Prefix every line of the quote with "> " for multi-line block-quotes
        quoted_lines = "\n> ".join(quote.splitlines())
        parts.append(f"**{L['quote']}**:\n> {quoted_lines}\n")
        parts.append(f"**{L['feedback']}**:\n{feedback}\n")
        parts.append("---\n")

    return "\n".join(parts)
