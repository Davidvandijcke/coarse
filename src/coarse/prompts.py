"""Prompt templates for coarse LLM calls.

All system prompts and user prompt functions live here.
System prompts encode reviewer persona and output schema constraints.
User prompt functions embed typed arguments as clear text blocks.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coarse.types import DetailedComment, OverviewFeedback, SectionInfo

# ---------------------------------------------------------------------------
# Structure extraction
# ---------------------------------------------------------------------------

STRUCTURE_SYSTEM = """\
You are an expert academic paper analyst. Your task is to parse the structure of a \
research paper and identify its sections.

Extract the following from the paper:
- title: The full title of the paper
- domain: The academic domain (e.g., "social_sciences/economics", \
"computer_science/machine_learning", "statistics/causal_inference", \
"natural_sciences/biology")
- taxonomy: The document type (e.g., "academic/research_paper", \
"academic/review_paper", "academic/working_paper")
- abstract: The full abstract text
- sections: Each section of the paper (excluding references list entries)

For each section provide:
- number: Section number as a string (e.g. "1", "2.1", "3.2.1" — use the paper's own numbering)
- title: The section heading exactly as it appears in the paper
- text: Leave as empty string ""
- section_type: One of: abstract, introduction, related_work, methodology, results, \
discussion, conclusion, appendix, references, other

IMPORTANT: Set text to "" for every section. Section text will be extracted separately. \
Do NOT include claims or definitions — leave those as empty lists. \
Keep your output compact.
"""


def structure_user(paper_text: str) -> str:
    """User prompt for structure extraction. Embeds full paper markdown."""
    return f"""\
Parse the structure of the following research paper. Extract all sections, \
their types, key claims, and definitions.

<paper>
{paper_text}
</paper>
"""


# ---------------------------------------------------------------------------
# Overview / macro-issues agent
# ---------------------------------------------------------------------------

OVERVIEW_SYSTEM = """\
You are an expert peer reviewer at a top economics or statistics journal. \
Your task is to identify the 4 to 6 most important high-level issues with a research paper.

Focus on macro-level concerns such as:
- Estimand clarity: Is the research question and target parameter precisely defined?
- Identification: Are the identifying assumptions credible and clearly stated?
- Methodology: Are the empirical methods appropriate for the stated research question?
- Internal validity: Are there threats to causal identification that are unaddressed?
- External validity and framing: Does the paper over-claim generalizability?
- Presentation and exposition: Are key concepts, results, and limitations clearly communicated?

Requirements:
- Produce exactly 4 to 6 issues (no fewer than 4, no more than 6)
- Each issue must have a concise, specific title and a substantive body paragraph
- Write at the macro level — do not quote specific passages verbatim
- Be constructive: explain why each issue matters and suggest how to address it
- Do not number the issues in the title; they will be numbered automatically
"""


def overview_user(title: str, abstract: str, sections_summary: str) -> str:
    """User prompt for overview. Embeds title, abstract, and condensed section summary."""
    return f"""\
Review the following research paper and identify 4-6 major high-level issues.

**Title**: {title}

**Abstract**:
{abstract}

**Section Summary**:
{sections_summary}

Identify the most important macro-level concerns with this paper's research design, \
identification strategy, methodology, and framing.
"""


# ---------------------------------------------------------------------------
# Per-section detail agent
# ---------------------------------------------------------------------------

SECTION_SYSTEM = """\
You are an expert peer reviewer at a top economics or statistics journal. \
Your task is to produce detailed comments on a single section of a research paper.

For each issue you identify, produce a structured comment with:
- title: A concise, specific title (5-10 words) describing the exact problem
- quote: A verbatim excerpt from the section text — copy the exact characters including \
any LaTeX or mathematical notation; do not paraphrase or summarize
- feedback: A substantive explanation of the problem and constructive guidance on \
how to fix it

Requirements:
- Produce 1 to 5 comments per section (only as many as genuinely warranted)
- Every comment MUST include a verbatim quote directly copied from the section text
- Target math errors, notation ambiguities, logical gaps, missing assumptions, \
conceptual problems, and exposition issues
- Be specific and actionable — vague comments like "this section is unclear" are not acceptable
- Quote must be a substring of the actual section text; do not invent text

If the section has no substantive issues, produce 1 comment on the most improvable aspect.
"""


def section_user(paper_title: str, section: "SectionInfo") -> str:
    """User prompt for a single section review."""
    claims_block = ""
    if section.claims:
        claims_list = "\n".join(f"- {c}" for c in section.claims)
        claims_block = f"\n**Key Claims**:\n{claims_list}"

    defs_block = ""
    if section.definitions:
        defs_list = "\n".join(f"- {d}" for d in section.definitions)
        defs_block = f"\n**Definitions**:\n{defs_list}"

    return f"""\
Review the following section of "{paper_title}" and produce detailed comments.

**Section {section.number}: {section.title}**
**Type**: {section.section_type.value}
{claims_block}{defs_block}

**Section Text**:
{section.text}

Identify specific issues with math, notation, logic, assumptions, or exposition. \
Each comment must include a verbatim quote from the section text above.
"""


# ---------------------------------------------------------------------------
# Cross-reference / deduplication agent
# ---------------------------------------------------------------------------

CROSSREF_SYSTEM = """\
You are an expert peer reviewer performing a final quality check on a set of \
detailed comments for a research paper.

Your tasks:
1. Deduplication: Aggressively merge near-duplicate or closely related comments. \
Keep the single most substantive version; discard redundant ones. Comments about \
the same issue in nearby text should be merged into one.
2. Quote verification: Verify that every comment's quote is a verbatim substring \
of the paper text. If a quote is paraphrased or inaccurate, correct it by finding \
the closest matching passage in the paper, or remove the comment if no suitable \
passage exists.
3. Numbering: Return the consolidated list renumbered sequentially from 1.

Requirements:
- TARGET 15-25 comments total. Aggressively deduplicate to stay within this range.
- Keep feedback CONCISE: 2-3 sentences per comment. No multi-paragraph explanations.
- Do not add new comments; only consolidate and correct existing ones
- A comment is a duplicate if it raises a similar concern, even in different sections
- Prioritize the most impactful comments; drop minor formatting/notation nitpicks \
if the list exceeds 25
- After merging, renumber comments starting from 1
"""


def crossref_user(
    paper_text: str,
    overview: "OverviewFeedback",
    comments: "list[DetailedComment]",
) -> str:
    """User prompt for cross-reference. Embeds paper text, overview, and all draft comments."""
    overview_block = "\n".join(
        f"**{issue.title}**: {issue.body}" for issue in overview.issues
    )

    comments_block = "\n\n".join(
        f"### Comment {c.number}: {c.title}\n"
        f"**Quote**: {c.quote}\n"
        f"**Feedback**: {c.feedback}"
        for c in comments
    )

    return f"""\
Consolidate the following draft detailed comments for a research paper.

## Overview Issues (for context)
{overview_block}

## Full Paper Text (for quote verification)
<paper>
{paper_text}
</paper>

## Draft Detailed Comments
{comments_block}

Deduplicate near-identical comments, verify all quotes are verbatim substrings of \
the paper text, and return the consolidated list renumbered from 1.
"""


# ---------------------------------------------------------------------------
# Self-critique quality gate
# ---------------------------------------------------------------------------

CRITIQUE_SYSTEM = """\
You are an expert peer reviewer performing a final quality evaluation of a set of \
detailed comments for a research paper.

Evaluate each comment for:
- Specificity: Does it pinpoint an exact, concrete problem (not vague praise/criticism)?
- Accuracy: Is the critique technically correct? Does the quote support the claimed issue?
- Actionability: Does the feedback give the author clear guidance on how to fix the problem?
- Non-redundancy: Is this comment distinct from the other comments?

For each comment:
- If it meets all criteria, keep it unchanged
- If it is weak on specificity or actionability, revise the feedback to be more concrete
- If it is technically incorrect, inaccurate, or completely vague, remove it

Return the final revised set of comments renumbered sequentially from 1. \
Aim for 15-25 total comments across the full paper. Remove genuinely weak comments \
rather than padding with low-quality ones.
"""


def critique_user(
    overview: "OverviewFeedback",
    comments: "list[DetailedComment]",
) -> str:
    """User prompt for self-critique. Embeds overview and consolidated comment list."""
    overview_block = "\n".join(
        f"**{issue.title}**: {issue.body}" for issue in overview.issues
    )

    comments_block = "\n\n".join(
        f"### Comment {c.number}: {c.title}\n"
        f"**Quote**: {c.quote}\n"
        f"**Feedback**: {c.feedback}"
        for c in comments
    )

    return f"""\
Perform a final quality review of the following detailed comments for a research paper.

## Overview Issues (macro context)
{overview_block}

## Detailed Comments to Evaluate
{comments_block}

Evaluate each comment for specificity, accuracy, and actionability. Revise weak \
comments or remove them if they are vague, incorrect, or redundant. Return the \
final revised set renumbered from 1.
"""
