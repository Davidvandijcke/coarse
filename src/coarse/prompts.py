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

Focus on substantive concerns, prioritized by severity:
1. **Fundamental flaws**: Mathematical errors, invalid proofs, flawed identification \
strategies, estimands that don't match the stated research question
2. **Theory-empirics mismatches**: Do theoretical assumptions (i.i.d., continuity, \
monotonicity, etc.) actually hold given the data and empirical design? Does the \
simulation DGP match the theoretical claims? Are methods used that contradict stated \
assumptions?
3. **Estimand and interpretation**: Is the target parameter precisely defined? Are \
causal claims supported by the identification strategy? Are comparisons with existing \
methods fair and accurate?
4. **Gaps in the argument**: Missing cases, unaddressed threats to validity, unstated \
regularity conditions that the proofs rely on

Do NOT focus on: formatting, notation preferences, minor exposition issues, or \
stylistic choices that don't affect correctness.

Requirements:
- Produce exactly 4 to 6 issues (no fewer than 4, no more than 6)
- Each issue must have a concise, specific title and a substantive body paragraph
- Write at the macro level — do not quote specific passages verbatim
- For each issue: (a) state the problem, (b) explain its consequences for the \
paper's main claims, (c) suggest a specific remedy
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

Prioritize issues by severity:
(a) Incorrect or unsubstantiated claims — math errors, flawed logic, missing \
assumptions that invalidate results
(b) Theory-practice gaps — assumptions unlikely to hold, methods that don't match \
the stated estimand, simulation designs that don't test the claimed properties
(c) Unclear definitions that affect interpretation of main results
(d) Exposition issues ONLY if they cause genuine confusion about the contribution

Do NOT comment on: formatting, LaTeX rendering artifacts, minor notation preferences, \
or stylistic choices that don't affect correctness.

Requirements:
- Produce 1 to 5 comments per section (only as many as genuinely warranted)
- Every comment MUST include a verbatim quote directly copied from the section text
- Quote must be a substring of the actual section text; do not invent text
- For each issue: state what is wrong, explain why it matters for the paper's \
claims, and suggest a specific fix — not "clarify this" but "rewrite X as Y because Z"

If the section has no substantive issues, produce 1 comment on the most improvable aspect.
"""


def section_user(
    paper_title: str,
    section: "SectionInfo",
    overview: "OverviewFeedback | None" = None,
) -> str:
    """User prompt for a single section review.

    If overview is provided, includes macro-level issues as context so the
    section agent can connect its findings to broader paper concerns.
    """
    claims_block = ""
    if section.claims:
        claims_list = "\n".join(f"- {c}" for c in section.claims)
        claims_block = f"\n**Key Claims**:\n{claims_list}"

    defs_block = ""
    if section.definitions:
        defs_list = "\n".join(f"- {d}" for d in section.definitions)
        defs_block = f"\n**Definitions**:\n{defs_list}"

    context_block = ""
    if overview and overview.issues:
        issues_list = "\n".join(
            f"- **{issue.title}**: {issue.body[:200]}" for issue in overview.issues
        )
        context_block = f"""
**Paper-Level Issues (for context)**:
The overview review identified these macro concerns. Check whether this section \
contributes to or could help address any of them:
{issues_list}
"""

    return f"""\
Review the following section of "{paper_title}" and produce detailed comments.

**Section {section.number}: {section.title}**
**Type**: {section.section_type.value}
{claims_block}{defs_block}{context_block}

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

Assign a severity to each surviving comment:
- "critical": invalidates a claim, proof error, fundamental methodology flaw, flawed \
identification strategy
- "major": weakens an argument, missing important case, unclear estimand definition, \
theory-practice mismatch
- "minor": notation, exposition, style, or issues that don't affect the paper's main claims

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

Evaluate each comment for specificity, accuracy, and actionability. Assign severity \
(critical/major/minor) to each surviving comment. Revise weak comments or remove \
them if they are vague, incorrect, or redundant. Return the final revised set \
renumbered from 1.
"""


# ---------------------------------------------------------------------------
# Assumption checker (theory-vs-empirics consistency)
# ---------------------------------------------------------------------------

ASSUMPTION_CHECK_SYSTEM = """\
You are an expert methodologist checking whether a research paper's theoretical \
assumptions are consistent with its empirical implementation.

For each stated assumption in the paper, check:
1. Does the data structure satisfy the assumption? (e.g., i.i.d. assumed but \
panel/clustered data used; stationarity assumed but trending data)
2. Does the empirical implementation respect the assumption? (e.g., uniform \
kernel assumed but triangular used; parametric form assumed but nonparametric \
estimation)
3. Does the simulation DGP match the theoretical conditions? (e.g., does the \
DGP satisfy the assumptions under which theorems are proved?)

Common violations to look for:
- i.i.d. vs panel/time-series data structure
- Continuity/smoothness assumptions vs discrete outcomes
- Monotonicity assumptions that collapse to degenerate cases
- Rate conditions that require uniform convergence but are stated pointwise
- Bandwidth/tuning parameter choices that don't match theoretical requirements

Report 0 to 3 issues. Only report genuine mismatches — do not flag assumptions \
that are clearly satisfied. Each issue must have a specific title and body \
explaining the mismatch and its consequences.
"""


def assumption_check_user(title: str, sections_text: str) -> str:
    """User prompt for assumption consistency check."""
    return f"""\
Check whether the theoretical assumptions in "{title}" are consistent with \
the empirical methodology and simulation design.

<paper_sections>
{sections_text}
</paper_sections>

Identify any mismatches between stated assumptions and the actual data, methods, \
or simulations used. Report 0-3 issues, each with a title and body.
"""
