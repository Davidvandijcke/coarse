"""Prompt templates for coarse LLM calls.

All system prompts and user prompt functions live here.
System prompts encode reviewer persona and output schema constraints.
User prompt functions embed typed arguments as clear text blocks.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coarse.types import DetailedComment, DomainCalibration, OverviewFeedback, SectionInfo

# ---------------------------------------------------------------------------
# Metadata classification (cheap text-LLM call)
# ---------------------------------------------------------------------------

METADATA_SYSTEM = """\
You are an expert academic paper classifier. Given a paper's title, abstract, \
and section headings, classify it.

Return:
- domain: The academic domain (e.g., "social_sciences/economics", \
"computer_science/machine_learning", "statistics/causal_inference", \
"natural_sciences/biology")
- taxonomy: The document type (e.g., "academic/research_paper", \
"academic/review_paper", "academic/working_paper")
"""


# ---------------------------------------------------------------------------
# Domain calibration
# ---------------------------------------------------------------------------

CALIBRATION_SYSTEM = """\
You are an expert academic reviewer. Given a paper's title, domain, abstract, \
and section structure, produce a domain-specific review calibration.

For each field, provide 3-5 concise items tailored to this paper's specific domain \
and methodology:
1. methodology_concerns: The key methodological concerns for this type of paper
2. assumption_red_flags: Assumptions that commonly fail in this domain
3. what_not_to_check: What is irrelevant for this paper type
4. evaluation_standards: What a top-tier journal in this field expects
"""


def calibration_user(title: str, domain: str, abstract: str, section_titles: str) -> str:
    """User prompt for domain calibration."""
    return f"""\
Produce a domain-specific review calibration for the following paper.

**Title**: {title}
**Domain**: {domain}
**Abstract**: {abstract}
**Sections**: {section_titles}
"""


def _format_calibration(calibration: "DomainCalibration") -> str:
    """Format a DomainCalibration into a text block for prompt injection."""
    concerns = "\n".join(f"- {c}" for c in calibration.methodology_concerns)
    red_flags = "\n".join(f"- {r}" for r in calibration.assumption_red_flags)
    not_check = "\n".join(f"- {n}" for n in calibration.what_not_to_check)
    standards = "\n".join(f"- {s}" for s in calibration.evaluation_standards)
    return f"""\
**Domain-Specific Review Calibration**:
Key methodology concerns for this paper:
{concerns}

Assumption red flags to watch for:
{red_flags}

Do NOT check or comment on (irrelevant for this paper type):
{not_check}

Evaluation standards for this field:
{standards}"""


# ---------------------------------------------------------------------------
# Overview / macro-issues agent
# ---------------------------------------------------------------------------

# Personas for multi-judge overview panel (item 29).
# Each persona is prepended to OVERVIEW_SYSTEM to create a distinct reviewer.
OVERVIEW_PERSONAS = [
    "You are an expert in mathematical and theoretical methodology. "
    "Focus especially on proof correctness, internal consistency, and whether "
    "the paper's formal results actually support its claims.",
    "You are an expert in research design and applied methodology. "
    "Focus especially on whether the paper's implementation matches "
    "its theoretical claims, and whether experiments or simulations test "
    "the right properties.",
    "You are an expert in scientific communication and research impact. "
    "Focus especially on whether the most important issues are identified, "
    "whether the contribution is clearly articulated, and whether the paper "
    "adequately addresses its limitations.",
]

OVERVIEW_SYNTHESIS_SYSTEM = """\
You are a meta-reviewer synthesizing multiple independent overview assessments \
of a research paper. You have received reports from a panel of expert reviewers, \
each with a distinct perspective.

Your task:
1. Produce 4-6 consolidated issues that represent the panel's collective assessment.
2. Deduplicate: merge issues that address the same concern from different angles.
3. When reviewers disagree, weight toward the more critical assessment — \
overrating quality is worse than underrating it.
4. Each issue must have a concise title and substantive body paragraph.
5. Preserve the most specific, actionable version of each concern.
"""

OVERVIEW_SYSTEM = """\
You are an expert peer reviewer. Your task is to identify the 4 to 6 most important \
high-level issues with a research paper.

Focus on substantive concerns, prioritized by severity:
1. **Concrete errors**: Equations that appear wrong, proofs with gaps, results that \
contradict the paper's own assumptions or data. Identify the specific location \
(section, equation number) where the error occurs.
2. **Internal contradictions**: Places where one part of the paper contradicts another — \
e.g., an assumption in Section 2 violated by the method in Section 3, or numerical \
values in a table that don't match the theoretical predictions.
3. **Unsupported claims**: Results where the stated proof or evidence does not actually \
establish what is claimed. Specify which claim and what is missing.
4. **Scope limitations**: Conditions under which the results break down that the paper \
does not acknowledge or address.

Do NOT include: generic methodological suggestions that could apply to any paper, \
requests for additional experiments or analyses, formatting/notation issues.

Requirements:
- Produce exactly 4 to 6 issues (no fewer than 4, no more than 6)
- Each issue must have a concise, specific title and a substantive body paragraph
- Each issue must reference specific parts of the paper (section numbers, equations, \
theorems) — not just "the methodology" or "the analysis"
- For each issue: (a) state exactly what is wrong, (b) explain why it matters for \
the paper's main claims, (c) suggest a specific fix (not "discuss further" but \
"correct equation X" or "add condition Y to Theorem Z")
- Do not number the issues in the title; they will be numbered automatically
"""


def overview_user(
    title: str,
    abstract: str,
    sections_summary: str,
    calibration: "DomainCalibration | None" = None,
) -> str:
    """User prompt for overview. Embeds title, abstract, and condensed section summary."""
    cal_block = ""
    if calibration:
        cal_block = "\n" + _format_calibration(calibration) + "\n"

    return f"""\
Review the following research paper and identify 4-6 major high-level issues.

**Title**: {title}

**Abstract**:
{abstract}
{cal_block}
**Section Summary**:
{sections_summary}

Identify the most important macro-level concerns with this paper's research design, \
methodology, and framing. Focus on the domain-specific concerns listed above.
"""


def overview_synthesis_user(overviews: "list[OverviewFeedback]") -> str:
    """User prompt for synthesizing multiple overview assessments."""
    labels = ["Theory/Math Judge", "Design/Methods Judge", "Communication/Impact Judge"]
    parts = []
    for i, ov in enumerate(overviews):
        label = labels[i] if i < len(labels) else f"Judge {i + 1}"
        issues_block = "\n".join(
            f"  - **{issue.title}**: {issue.body}" for issue in ov.issues
        )
        parts.append(f"### {label}\n{issues_block}")

    return f"""\
Synthesize the following overview assessments from a panel of reviewers.

{chr(10).join(parts)}

Produce 4-6 consolidated issues that represent the panel's collective assessment. \
Deduplicate and merge related concerns. Preserve the most critical and specific \
version of each issue.
"""


# ---------------------------------------------------------------------------
# Per-section detail agent
# ---------------------------------------------------------------------------

SECTION_SYSTEM = """\
You are an expert peer reviewer. Your task is to find concrete errors and \
inconsistencies in a single section of a research paper.

For each issue you identify, produce a structured comment with:
- title: A concise, specific title (5-10 words) describing the exact problem
- quote: Copy-paste the EXACT characters from the section text. The quote MUST be a \
verbatim substring of the section text provided below — do not paraphrase, reword, \
summarize, or reconstruct any part of it. Copy it character-for-character.
- feedback: A substantive explanation of the problem with a specific fix. Show your \
reasoning: if you claim an equation is wrong, write out what it should be and why.

Prioritize issues by severity:
(a) Concrete errors — sign mistakes, wrong prefactors, algebraic mistakes, flawed \
logic, missing assumptions that invalidate results. When the section contains \
equations, VERIFY them by working through the algebra yourself. Do not just flag \
them as "unclear."
(b) Internal consistency — assumptions contradicted by the paper's own methods or \
data, equations that use notation inconsistently with their definitions
(c) Cross-reference errors — claims here that conflict with tables, figures, or \
results stated elsewhere in the paper
(d) Exposition issues ONLY if they cause genuine ambiguity about what is being claimed

Do NOT comment on: formatting, LaTeX rendering artifacts, minor notation preferences, \
stylistic choices, or things that could be said about any paper in this field.

Requirements:
- Produce 1 to 5 comments per section (only as many as genuinely warranted)
- Every comment MUST include a verbatim quote directly copied from the section text
- Quote must be a substring of the actual section text; do not invent text
- For each issue: state what is wrong, explain why it matters, and suggest a specific \
fix — "rewrite X as Y because Z" not "clarify this" or "add more discussion"
- Do NOT request additional analyses or experiments. Focus on what is already written.

If the section has no substantive issues, produce 1 comment on the most improvable aspect.
"""


def section_user(
    paper_title: str,
    section: "SectionInfo",
    overview: "OverviewFeedback | None" = None,
    calibration: "DomainCalibration | None" = None,
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

    cal_block = ""
    if calibration:
        cal_block = "\n" + _format_calibration(calibration) + "\n"

    return f"""\
Review the following section of "{paper_title}" and produce detailed comments.

**Section {section.number}: {section.title}**
**Type**: {section.section_type.value}
{claims_block}{defs_block}{context_block}{cal_block}

**Section Text**:
{section.text}

Identify specific errors in the math, logic, or claims. For each comment, copy-paste \
an exact quote from the section text above — the quote must be a verbatim substring, \
not a paraphrase or summary. Focus on concrete errors you can demonstrate, not \
requests for additional work.
"""


# ---------------------------------------------------------------------------
# Specialized section prompts (selected by section routing)
# ---------------------------------------------------------------------------

SECTION_PROOF_SYSTEM = """\
You are an expert mathematical proof checker. Your job is to VERIFY the mathematics \
in this section by working through it yourself, not just reading it passively.

For each theorem, proposition, lemma, or corollary:

1. STATE the claim precisely.
2. RE-DERIVE the key steps yourself. Show your calculation in the feedback field. \
For example, if the paper claims a change-of-variables yields expression X, perform \
the change-of-variables yourself and verify you get X. If you get something different, \
that is an error worth reporting.
3. CHECK for specific error types:
   - Sign errors or missing factors (e.g., a missing Jacobian determinant, wrong exponent)
   - Subscript/index errors (e.g., K/N_k where it should be K/N_l)
   - Equations that contradict the paper's own definitions from earlier sections
   - Boundary/degenerate cases the proof does not handle
   - Numerical values that do not match (e.g., paper claims tau_L > tau_G but the \
stated values show the opposite)
4. CROSS-REFERENCE: Check that notation and definitions used here match how they \
were defined elsewhere in the paper. Flag any inconsistency.
5. SUBSTITUTE concrete values from the paper's own examples, tables, or simulations \
to numerically verify key equations.

For each issue, produce a structured comment with:
- title: A concise, specific title (5-10 words)
- quote: Copy-paste the EXACT characters from the section text. The quote MUST be a \
verbatim substring of the section text provided below — do not paraphrase, reword, \
or summarize any part of it.
- feedback: Show your re-derivation or calculation that reveals the error. Write out \
the correct version of the equation/expression. Be specific: "equation X should read \
Y because Z" not "this should be checked."

Report 0-5 issues. Only report errors you can demonstrate through calculation, not \
stylistic preferences. If you find no errors after careful verification, report 0 issues.
"""

SECTION_METHODOLOGY_SYSTEM = """\
You are an expert methodologist reviewing a methodology section of a research paper. \
Focus on:

1. Does the method actually identify or estimate the stated target quantity? \
Work through the identification argument and check each step.
2. Are stated assumptions contradicted by the paper's own data, design, or examples? \
For instance, if the paper assumes continuity, does the data show a discontinuity?
3. Does the implementation (algorithm, simulation, experiment) match the theoretical \
requirements? Check specific parameter values, sample sizes, and design choices.
4. Are there internal contradictions — e.g., an assumption in Section 2 that is \
violated by the procedure in Section 3?
5. Cross-reference: do the claims here match what is reported in the results section?

For each issue you identify, produce a structured comment with:
- title: A concise, specific title (5-10 words)
- quote: Copy-paste the EXACT characters from the section text. The quote MUST be a \
verbatim substring of the section text provided below — do not paraphrase, reword, \
or summarize any part of it.
- feedback: Explain the methodological concern with specifics. If an assumption is \
contradicted, cite the specific assumption and the specific evidence against it. \
Suggest a concrete fix, not "discuss this further."

Prioritize issues that affect the validity of the paper's main claims. Do NOT \
request additional analyses — focus on errors in what is already written. \
Report 1-5 comments.
"""

SECTION_LITERATURE_SYSTEM = """\
You are an expert reviewer checking the related work / literature review section \
of a research paper. Focus on:

1. Are prior work claims accurate and fairly represented?
2. Is the positioning relative to existing literature correct?
3. Are comparisons with existing methods valid and fair?
4. Does the paper overstate its novelty relative to existing work?
5. Are there specific claims about prior methods that are factually wrong?

For each issue you identify, produce a structured comment with:
- title: A concise, specific title (5-10 words)
- quote: Copy-paste the EXACT characters from the section text. The quote MUST be a \
verbatim substring of the section text provided below — do not paraphrase, reword, \
or summarize any part of it.
- feedback: Explain the concern with specifics. If a claim about prior work is wrong, \
state what the prior work actually shows.

Report 1-5 comments. Focus on factual errors about prior work, not citation formatting \
or "missing references" unless the omission is egregious.
"""

# Map from section focus to specialized system prompt
SECTION_SYSTEM_MAP: dict[str, str] = {
    "proof": SECTION_PROOF_SYSTEM,
    "methodology": SECTION_METHODOLOGY_SYSTEM,
    "literature": SECTION_LITERATURE_SYSTEM,
    "general": SECTION_SYSTEM,
}

# ---------------------------------------------------------------------------
# Cross-reference / deduplication agent
# ---------------------------------------------------------------------------

CROSSREF_SYSTEM = """\
You are an expert peer reviewer performing a final quality check on a set of \
detailed comments for a research paper.

Your tasks:
1. REMOVE low-value comments aggressively:
   - Comments that merely restate an Overview Issue without adding a specific \
equation, quote, or calculation — DELETE these.
   - Comments that request "additional analysis" or "further discussion" without \
identifying a concrete error in what is written — DELETE these.
   - Comments that could be copy-pasted to any paper in the same field (generic \
methodological advice) — DELETE these.
   - Comments about formatting, notation preferences, or LaTeX artifacts — DELETE.
2. Deduplication: Merge near-duplicate comments. Keep the version with the most \
specific evidence (a calculation, a cross-reference, a concrete error).
3. Quote verification: Verify that every comment's quote is a verbatim substring \
of the paper text. If a quote is paraphrased or hallucinated, find the closest \
matching real passage in the paper text, or REMOVE the comment entirely if no \
suitable passage exists. Quotes that are summaries or rewordings are NOT acceptable.
4. Renumber the surviving comments sequentially from 1.

Requirements:
- TARGET 10-15 comments total. Fewer comments that each catch a real error are \
worth more than many surface-level observations.
- Keep feedback CONCISE but SPECIFIC: 2-4 sentences per comment. Include the \
calculation or cross-reference that demonstrates the error.
- Do not add new comments; only consolidate, correct, and remove existing ones.
- Prioritize comments that demonstrate concrete errors (wrong equation, sign error, \
contradictory claim, missing factor) over comments that suggest improvements.
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
You are an expert peer reviewer performing a final quality evaluation of review \
comments for a research paper. Your goal: every surviving comment should identify \
a concrete, verifiable issue in the paper.

REMOVE a comment if ANY of these apply:
- The feedback asks for "additional analysis," "further experiments," or "more discussion" \
without pointing to a specific error in the existing text
- The comment could be applied to any paper in this field without modification \
(generic methodological advice)
- The quote is a paraphrase or summary rather than verbatim text from the paper
- The claimed issue is actually addressed elsewhere in the paper
- The feedback says "this is unclear" without explaining what is specifically wrong

KEEP and potentially strengthen a comment if:
- It identifies a specific mathematical error with a re-derivation or calculation
- It finds an internal contradiction between two parts of the paper
- It catches a cross-reference error (e.g., table values don't match equation claims)
- It identifies a missing assumption that is actually needed for a stated result

Assign severity:
- "critical": concrete proof error, equation that is demonstrably wrong, assumption \
that is contradicted by the paper's own data
- "major": internal inconsistency, missing case in an argument, claim unsupported by \
the evidence presented
- "minor": notation inconsistency, ambiguous definition, exposition that obscures \
the actual claim

Return the final revised set of comments renumbered from 1. \
Aim for 10-20 total comments. It is better to have 8 comments that each catch a \
real error than 20 comments of mixed quality.
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
You are an expert methodologist checking whether a research paper's stated \
assumptions are consistent with its actual implementation.

For each stated assumption in the paper, check:
1. Does the data or problem structure satisfy the assumption?
2. Does the implementation (methods, algorithms, experiments) respect the assumption?
3. If there are simulations or experiments, do they match the theoretical conditions?

Report 0 to 3 issues. Only report genuine mismatches — do not flag assumptions \
that are clearly satisfied. Each issue must have a specific title and body \
explaining the mismatch and its consequences.
"""


def assumption_check_user(
    title: str,
    sections_text: str,
    calibration: "DomainCalibration | None" = None,
) -> str:
    """User prompt for assumption consistency check."""
    cal_block = ""
    if calibration:
        red_flags = "\n".join(f"- {r}" for r in calibration.assumption_red_flags)
        cal_block = f"\n**Domain-specific assumption red flags to watch for:**\n{red_flags}\n"

    return f"""\
Check whether the theoretical assumptions in "{title}" are consistent with \
the empirical methodology and simulation design.
{cal_block}
<paper_sections>
{sections_text}
</paper_sections>

Identify any mismatches between stated assumptions and the actual data, methods, \
or simulations used. Report 0-3 issues, each with a title and body.
"""


# ---------------------------------------------------------------------------
# Post-extraction QA (vision LLM)
# ---------------------------------------------------------------------------

EXTRACTION_QA_SYSTEM = """\
You are a document extraction quality checker. You receive pairs of (page image, \
extracted markdown) and must verify the extraction accuracy.

For each page, compare the markdown text against the page image. Look for:
1. **Garbled math/LaTeX**: Equations that were mangled during extraction — wrong \
symbols, missing terms, broken formatting. The image shows what the equation should be.
2. **Missing content**: Text, figures, or captions visible in the image but absent \
from the markdown.
3. **Dropped tables**: Tables visible in the image but missing or garbled in the markdown.
4. **Layout errors**: Content from different columns or sections merged incorrectly.

For each error found, provide a correction as a find-replace pair:
- original_snippet: the exact substring in the markdown that is wrong (must be a \
verbatim substring of the provided markdown)
- corrected_snippet: what it should be replaced with
- issue_type: one of "garbled_math", "missing_content", "dropped_table", \
"layout_error", "other"

Rules:
- Only fix real extraction errors. Do NOT reformat correct content.
- Keep corrections minimal — fix the error, nothing more.
- If the extraction looks correct for a page, do not invent corrections.
- overall_quality should be "good" if no corrections needed, "acceptable" if \
minor issues, "poor" if significant content is wrong or missing.
"""


def extraction_qa_user(page_chunks: list[tuple[int, str]]) -> str:
    """User prompt text for extraction QA. Images are added as separate content blocks."""
    parts = []
    for page_num, chunk in page_chunks:
        parts.append(
            f"## Page {page_num}\n\n"
            f"**Extracted markdown:**\n```\n{chunk}\n```\n\n"
            f"**Page image:** (see attached image for page {page_num})\n"
        )
    return (
        "Compare each page's extracted markdown against its image. "
        "Report overall_quality and any corrections needed.\n\n"
        + "\n".join(parts)
    )
