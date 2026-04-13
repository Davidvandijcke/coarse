"""Canonical pipeline stage and estimation spec.

This module is the single source of truth for the review-stage heuristics that
must stay aligned across the Python runtime, the Python cost estimator, and the
web cost estimator.
"""

from __future__ import annotations

from coarse.models import REASONING_MODEL_PREFIXES, REASONING_MODEL_SUBSTRINGS

# Section sizing
TOKENS_PER_SECTION = 1200
MAX_REVIEWABLE_SECTIONS = 25
MIN_SECTIONS = 4
SECTION_PROMPT_OVERHEAD = 8000
OVERVIEW_INPUT_OVERHEAD = 3000

# PDF/file extraction
TOKENS_PER_PAGE = 250
OCR_COST_PER_PAGE = 0.002
EXTRACTION_QA_FLAT_COST = 0.035
EXTRACTION_QA_IMAGE_OVERHEAD = 5000

# Conditional-stage heuristics
MATH_SECTION_FRACTION = 0.2
CROSS_SECTION_MIN_SECTIONS = 6
MAX_CROSS_SECTION_CALLS = 3

# Comment/editorial heuristics
AVG_COMMENTS_PER_SECTION = 3
TOKENS_PER_COMMENT = 350
EDITORIAL_OVERHEAD = 5000
OVERVIEW_CONTEXT_OVERHEAD = 5000
REASONING_OVERHEAD_MULTIPLIER = 4

FIXED_STAGE_INPUT_TOKENS: dict[str, int] = {
    "metadata": 500,
    "math_detection": 2000,
    "calibration": 1500,
    "literature_query_gen": 1500,
    "literature_ranking": 4000,
    "contribution_extraction": 3000,
}

# Flat-fee stages
LITERATURE_FLAT_COST = 0.03

# Conservative multiplier applied to the final total.
COST_BUFFER = 1.30

# Structured-output budgets per stage kind.
STAGE_OUTPUT_TOKENS: dict[str, int] = {
    "metadata": 256,
    "math_detection": 1024,
    "calibration": 2048,
    "literature_query_gen": 512,
    "literature_ranking": 2048,
    "contribution_extraction": 2048,
    "overview": 8192,
    "completeness": 4096,
    "section": 10000,
    "proof_verify": 16384,
    "cross_section": 8192,
    "editorial": 24000,
    "extraction_qa": 4096,
}


def estimate_section_count(total_tokens: int) -> int:
    """Estimate the number of reviewable sections from paper length."""
    return max(
        MIN_SECTIONS,
        min(MAX_REVIEWABLE_SECTIONS, total_tokens // TOKENS_PER_SECTION),
    )


def clamp_section_count(section_count: int) -> int:
    """Clamp a caller-supplied section count to the safe runtime minimum."""
    return max(1, section_count)


def estimate_math_section_count(section_count: int) -> int:
    """Estimate how many reviewable sections will trigger proof verification."""
    return max(0, round(section_count * MATH_SECTION_FRACTION))


def estimate_cross_section_count(section_count: int) -> int:
    """Estimate how many cross-section synthesis calls will fire."""
    return min(MAX_CROSS_SECTION_CALLS, section_count // CROSS_SECTION_MIN_SECTIONS)


def export_web_spec() -> dict[str, object]:
    """Return the JSON-serializable subset consumed by the web estimator."""
    return {
        "tokensPerSection": TOKENS_PER_SECTION,
        "maxReviewableSections": MAX_REVIEWABLE_SECTIONS,
        "minSections": MIN_SECTIONS,
        "sectionPromptOverhead": SECTION_PROMPT_OVERHEAD,
        "overviewInputOverhead": OVERVIEW_INPUT_OVERHEAD,
        "tokensPerPage": TOKENS_PER_PAGE,
        "ocrCostPerPage": OCR_COST_PER_PAGE,
        "extractionQaFlatCost": EXTRACTION_QA_FLAT_COST,
        "extractionQaImageOverhead": EXTRACTION_QA_IMAGE_OVERHEAD,
        "mathSectionFraction": MATH_SECTION_FRACTION,
        "crossSectionMinSections": CROSS_SECTION_MIN_SECTIONS,
        "maxCrossSectionCalls": MAX_CROSS_SECTION_CALLS,
        "avgCommentsPerSection": AVG_COMMENTS_PER_SECTION,
        "tokensPerComment": TOKENS_PER_COMMENT,
        "editorialOverhead": EDITORIAL_OVERHEAD,
        "overviewContextOverhead": OVERVIEW_CONTEXT_OVERHEAD,
        "reasoningOverheadMultiplier": REASONING_OVERHEAD_MULTIPLIER,
        "fixedStageInputTokens": FIXED_STAGE_INPUT_TOKENS,
        "literatureFlatCost": LITERATURE_FLAT_COST,
        "costBuffer": COST_BUFFER,
        "stageOutputTokens": STAGE_OUTPUT_TOKENS,
        "reasoningModelPrefixes": list(REASONING_MODEL_PREFIXES),
        "reasoningModelSubstrings": list(REASONING_MODEL_SUBSTRINGS),
    }
