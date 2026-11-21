"""Apply the refutation gate to a review produced outside the agent roles.

The gate in ``orchestrator`` guards findings an investigator produced. This
module applies the same gate to a review the staged pipeline already produced,
which is what ``review_paper(refute=True)`` and ``coarse review --refute`` use.

It is separate because the measurement made it the primary use. Generation and
verification turned out to be complements rather than substitutes: the staged
pipeline led on coverage on both benchmark papers and also asserted the most
claims the paper does not support, while the agent-only arms reversed both. So
the gate earns its keep applied to the pipeline's output rather than replacing
it. See docs/AGENTIC_REVIEW.md for the paired per-comment measurement.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from coarse.agent.orchestrator import DEFAULT_MAX_PARALLEL, REFUTER_TOOL_BUDGET, _refute
from coarse.agent.runner import run_agent
from coarse.agent.tools import ToolBox
from coarse.agent.types import (
    AgentRunRecord,
    IssueVerdict,
    LedgerFinding,
    PaperAnchor,
    RefutationVerdict,
)
from coarse.agent.workspace import ReviewWorkspace
from coarse.llm import LLMClient
from coarse.prompts import AGENT_ISSUE_REFUTER_SYSTEM, agent_issue_refuter_user
from coarse.types import DetailedComment, OverviewFeedback, OverviewIssue, PaperStructure

logger = logging.getLogger(__name__)


def refute_comments(
    comments: list[DetailedComment],
    paper_markdown: str,
    structure: PaperStructure,
    client: LLMClient,
    *,
    max_parallel: int = DEFAULT_MAX_PARALLEL,
    workspace_root: str | None = None,
    language: str | None = None,
) -> tuple[list[DetailedComment], list[RefutationVerdict], list[AgentRunRecord]]:
    """Re-establish each comment of an existing review, dropping what fails.

    This is the refutation gate applied to comments the staged pipeline already
    produced, rather than to findings an investigator produced. It exists
    because of how the arms actually measured: the staged pipeline was the
    recall leader on both benchmark papers and also asserted the most claims
    the paper does not support, while the agent arms reversed both. Generation
    and verification are therefore better combined than substituted.

    Each refuter runs in a fresh context with the claim, its quote, and tool
    access to the whole paper, and must reproduce the defect from the paper to
    confirm it. A comment whose verdict is not ``confirmed`` is dropped; one
    whose claim was real but misstated is rewritten from
    ``corrected_claim``.

    Returns the surviving comments, the verdicts, and per-agent accounting.
    """
    if not comments:
        return [], [], []

    workspace = ReviewWorkspace.create(paper_markdown, structure, root=workspace_root)  # type: ignore[arg-type]
    records: list[AgentRunRecord] = []
    verdicts: list[RefutationVerdict] = []
    try:
        # Keyed on POSITION, not on ``comment.number``. This stage runs before
        # ``_renumber_comments``, so the numbers here are whatever the
        # editorial pass emitted; on the double-failure fallback path they are
        # raw section order with section-local numbering, where duplicates are
        # expected. Keying on the number collapsed the lookup maps and
        # misattributed verdicts between comments that shared one.
        as_findings = [
            LedgerFinding(
                finding_id=f"c{position:03d}",
                title=c.title,
                location="",
                claim=c.feedback,
                severity=c.severity,
                anchors=[PaperAnchor(section_id="", quote=c.quote)],
            )
            for position, c in enumerate(comments, start=1)
        ]
        by_id = {f.finding_id: c for f, c in zip(as_findings, comments, strict=True)}

        with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(as_findings)))) as pool:
            futures = {
                pool.submit(_refute, client, workspace, structure, f, language): f
                for f in as_findings
            }
            for fut in as_completed(futures):
                finding = futures[fut]
                try:
                    verdict, record = fut.result()
                except Exception:
                    logger.warning(
                        "refuter for comment %s failed; keeping the comment",
                        finding.finding_id,
                        exc_info=True,
                    )
                    continue
                records.append(record)
                if verdict is not None:
                    verdicts.append(verdict)

        kept: list[DetailedComment] = []
        by_verdict = {v.finding_id: v for v in verdicts}
        for finding in as_findings:
            comment = by_id[finding.finding_id]
            verdict = by_verdict.get(finding.finding_id)
            if verdict is None:
                # No verdict means the check could not run, not that the
                # comment is wrong. Keep it rather than silently losing a
                # finding to an infrastructure failure.
                logger.info("no verdict for comment %r; keeping it", comment.title)
                kept.append(comment)
                continue
            if verdict.verdict != "confirmed":
                logger.info(
                    "dropping comment %r (%s): %s",
                    comment.title,
                    verdict.verdict,
                    verdict.reasoning[:160],
                )
                continue
            update: dict = {"severity": verdict.severity_after_review, "confidence": "high"}
            if verdict.corrected_claim.strip():
                update["feedback"] = verdict.corrected_claim.strip()
            kept.append(comment.model_copy(update=update))

        logger.info(
            "refutation kept %d of %d comment(s)",
            len(kept),
            len(comments),
        )
        return kept, verdicts, records
    finally:
        workspace.cleanup()


def _refute_issue(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    index: int,
    issue: OverviewIssue,
    language: str | None = None,
) -> tuple[IssueVerdict | None, AgentRunRecord]:
    """Check one macro issue in a fresh context with whole-paper tools."""
    toolbox = ToolBox(workspace=workspace, max_calls=REFUTER_TOOL_BUDGET)
    result = run_agent(
        client,
        role="issue_refuter",
        agent_id=f"iss-{index:02d}",
        system=AGENT_ISSUE_REFUTER_SYSTEM,
        task=agent_issue_refuter_user(
            structure.title,
            issue.title,
            issue.body,
            abstract=structure.abstract,
            language=language,
        ),
        toolbox=toolbox,
        submit_model=IssueVerdict,
        submit_description="Submit your verdict on this one macro concern.",
        max_turns=14,
        max_tokens=8192,
    )
    verdict = result.result if isinstance(result.result, IssueVerdict) else None
    if verdict is not None:
        verdict.issue_index = index
    return verdict, result.record


#: Shown when every macro issue was refuted. ``OverviewFeedback`` requires at
#: least one issue, and substituting the least-bad refuted one would reinstate
#: a claim the paper contradicts, so the honest answer goes in instead.
NO_ISSUES_SURVIVED = OverviewIssue(
    title="No paper-level concern survived independent review",
    body=(
        "Each macro-level concern raised in the first pass was re-checked against "
        "the paper by an independent reviewer, and none was borne out. The detailed "
        "comments below stand on their own. This is not a statement that the paper "
        "has no paper-level weakness, only that this review did not establish one."
    ),
)


def _clean_narrowed_body(issue: OverviewIssue, rewritten: str) -> str | None:
    """Validate a narrowed issue body, or return None to keep the original.

    Two defects were found by reading the actual output rather than the
    verdicts, and neither is catchable in the prompt alone:

    * The rewritten body began by repeating the issue title, so the rendered
      review showed the title twice. Stripped here.
    * Every "narrowed" body on the benchmark papers came back LONGER than the
      one it replaced, against the prompt's explicit instruction to say less
      and never more. That makes the stage a rewriter rather than a verifier,
      which is a much larger behavioural change than it advertises and
      reintroduces exactly the "an agent writes new review content" risk the
      ledger link elsewhere exists to prevent. A body that is not shorter is
      therefore refused and the original kept.

    ``_LENGTH_TOLERANCE`` leaves room for prose that genuinely narrows while
    spending a few more characters on a qualifier.
    """
    body = rewritten.strip()
    if not body:
        return None

    title = issue.title.strip()
    if title and body.lower().startswith(title.lower()):
        body = body[len(title) :].lstrip(" .:\u2014-\n")

    if not body:
        return None
    if len(body) > len(issue.body) * _LENGTH_TOLERANCE:
        return None
    return body


#: How much longer than the original a "narrowed" body may be. Narrowing should
#: shorten; a small allowance covers a qualifier added while cutting a claim.
_LENGTH_TOLERANCE = 1.05


def refute_issues(
    issues: list[OverviewIssue],
    paper_markdown: str,
    structure: PaperStructure,
    client: LLMClient,
    *,
    max_parallel: int = DEFAULT_MAX_PARALLEL,
    workspace_root: str | None = None,
    language: str | None = None,
) -> tuple[list[OverviewIssue], list[IssueVerdict], list[AgentRunRecord]]:
    """Re-establish each macro issue, narrowing or dropping what fails.

    The complement of ``refute_comments``, and the change the measurement
    pointed at: with comments refuted, macro-issue precision lagged comment
    precision badly on both benchmark papers, so the surviving false criticism
    was in the overall feedback. Figures are in docs/AGENTIC_REVIEW.md.

    Unlike a comment, an issue is rarely wholly right or wholly wrong, so a
    ``partly_supported`` verdict replaces the body with the reviewer's narrowed
    version rather than dropping the issue. An issue is kept unchanged when the
    check could not run, so an infrastructure failure never silently deletes
    one.
    """
    if not issues:
        return [], [], []

    workspace = ReviewWorkspace.create(paper_markdown, structure, root=workspace_root)  # type: ignore[arg-type]
    records: list[AgentRunRecord] = []
    verdicts: list[IssueVerdict] = []
    try:
        with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(issues)))) as pool:
            futures = {
                pool.submit(_refute_issue, client, workspace, structure, i, issue, language): i
                for i, issue in enumerate(issues, start=1)
            }
            for fut in as_completed(futures):
                index = futures[fut]
                try:
                    verdict, record = fut.result()
                except Exception:
                    logger.warning(
                        "issue refuter %d failed; keeping the issue", index, exc_info=True
                    )
                    continue
                records.append(record)
                if verdict is not None:
                    verdicts.append(verdict)

        by_index = {v.issue_index: v for v in verdicts}
        kept: list[OverviewIssue] = []
        for i, issue in enumerate(issues, start=1):
            verdict = by_index.get(i)
            if verdict is None:
                logger.info("no verdict for issue %d (%s); keeping it", i, issue.title)
                kept.append(issue)
                continue
            if verdict.verdict == "refuted":
                logger.info("dropping issue %d (%s): %s", i, issue.title, verdict.reasoning[:160])
                continue
            if verdict.verdict == "partly_supported":
                narrowed = _clean_narrowed_body(issue, verdict.rewritten_body)
                if narrowed is None:
                    # Either no replacement text, or one that did not narrow.
                    # Keeping the original is the safe reading: the reviewer
                    # called the issue partly right, so dropping it would lose
                    # a concern it endorsed, and accepting an expanded rewrite
                    # would let this stage author review content.
                    logger.info(
                        "issue %d (%s) was not narrowed usably; keeping the original",
                        i,
                        issue.title,
                    )
                    kept.append(issue)
                    continue
                logger.info(
                    "narrowing issue %d (%s); dropped: %s",
                    i,
                    issue.title,
                    "; ".join(verdict.dropped_points)[:200] or "(unspecified)",
                )
                kept.append(issue.model_copy(update={"body": narrowed}))
                continue
            kept.append(issue)

        if issues and not kept:
            logger.warning("every macro issue was refuted; substituting an explicit notice")
            kept = [NO_ISSUES_SURVIVED]

        logger.info("refutation kept %d of %d macro issue(s)", len(kept), len(issues))
        return kept, verdicts, records
    finally:
        workspace.cleanup()


def refute_review(
    overview: OverviewFeedback,
    comments: list[DetailedComment],
    paper_markdown: str,
    structure: PaperStructure,
    client: LLMClient,
    *,
    max_parallel: int = DEFAULT_MAX_PARALLEL,
    language: str | None = None,
) -> tuple[OverviewFeedback, list[DetailedComment], list[AgentRunRecord]]:
    """Re-check both halves of a review, and return it with what survived.

    The single entry point the pipeline's ``refute`` stage uses. Each half
    fails independently: a failure in one is logged and leaves that half
    unverified rather than losing the other, because an unverified review is
    the status quo and a lost one is a regression.
    """
    records: list[AgentRunRecord] = []

    comments_before = len(comments)
    try:
        comments, _verdicts, comment_records = refute_comments(
            comments,
            paper_markdown,
            structure,
            client,
            max_parallel=max_parallel,
            language=language,
        )
        records.extend(comment_records)
        logger.info(
            "refutation: %d of %d comment(s) independently reproduced across %d agent(s)",
            len(comments),
            comments_before,
            len(comment_records),
        )
    except Exception:
        logger.warning("comment refutation failed; keeping the unverified comments", exc_info=True)

    issues_before = len(overview.issues)
    try:
        kept_issues, _issue_verdicts, issue_records = refute_issues(
            overview.issues,
            paper_markdown,
            structure,
            client,
            max_parallel=max_parallel,
            language=language,
        )
        records.extend(issue_records)
        overview = overview.model_copy(update={"issues": kept_issues})
        logger.info(
            "refutation: %d of %d macro issue(s) kept across %d agent(s)",
            len(kept_issues),
            issues_before,
            len(issue_records),
        )
    except Exception:
        logger.warning("issue refutation failed; keeping the unverified issues", exc_info=True)

    return overview, comments, records
