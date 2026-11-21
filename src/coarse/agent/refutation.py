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
import re
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
    confirm it. A comment whose verdict is not ``confirmed`` is dropped, and a
    comment that survives is published as the pipeline wrote it: this gate only
    ever removes. It does not apply the refuter's ``corrected_claim``, which
    was measured to be the source of its own apparent precision gain, some of
    it by retreating from an error claim to a request for clarification. The
    suggested wording stays on the returned verdict for a human to weigh.

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
            # Keep or drop, never rewrite. Applying ``corrected_claim`` was
            # measured to be where this stage's apparent precision gain came
            # from, and in the wrong way: the rewrites that passed the judge
            # included ones that retreated from "X is wrong" to "the paper
            # does not say how X was handled". That satisfies "is this claim
            # supported" while giving the author less, so the gain was partly
            # an artefact of the metric. The refuter's suggested wording is
            # returned on the verdict for a human to weigh, and not applied.
            #
            # Severity is only ever lowered. The field defaults to "major", so
            # applying it unconditionally rewrote the severity of every kept
            # comment, including raising a minor one the refuter never
            # considered.
            update: dict = {"confidence": "high"}
            rank = {"critical": 0, "major": 1, "minor": 2}
            if rank.get(verdict.severity_after_review, 1) > rank.get(comment.severity, 1):
                update["severity"] = verdict.severity_after_review
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


#: Below this, a narrowed issue has nothing substantive left and the
#: "narrowing" was a refutation in disguise.
_MIN_NARROWED_CHARS = 80

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


_WS_RE = re.compile(r"\s+")
#: Marks where a span was removed, so whitespace is tidied only at the cut.
_CUT = "\x00"
_CUT_RE = re.compile(r"\s*" + _CUT + r"\s*")
_BLANK_LINE_RE = re.compile(r"\n[ \t]*\n")
_EXCESS_BLANKS_RE = re.compile(r"\n{3,}")


def _normalize(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


def narrow_by_deletion(body: str, spans: list[str]) -> tuple[str, list[str], list[str]]:
    """Remove *spans* from *body*, returning the result and what was and was not found.

    The only edit the refuter can make to an issue. Asking for a replacement
    body instead produced a rewrite longer than the original every time on the
    benchmark papers, prefixed with the issue title, which made the stage an
    author of review content rather than a verifier of it. Deleting named spans
    leaves every surviving word the reviewer's own and is checkable: a span
    either occurs in the body or it does not.

    Matching is exact first, then whitespace-insensitive, because a model
    re-wraps a sentence it quotes. A span that still does not match is reported
    rather than guessed at, so a hallucinated span removes nothing.

    Whitespace is tidied only at the cut. Collapsing the whole body was the
    first implementation and it flattened paragraph breaks and the newlines
    inside display math into one run-on block, which damages every narrowed
    issue whether or not the deletion itself was right.
    """
    removed: list[str] = []
    missing: list[str] = []
    out = body
    for span in spans:
        candidate = span.strip()
        if len(candidate) < 15:
            # Too short to identify a claim, and likely to match incidentally.
            missing.append(span)
            continue
        if candidate in out:
            out = out.replace(candidate, _CUT, 1)
            removed.append(candidate)
            continue
        norm_target = _normalize(candidate)
        if _normalize(out).find(norm_target) < 0:
            missing.append(span)
            continue
        out = _rebuild_without(out, norm_target)
        removed.append(candidate)
    return _close_cuts(out), removed, missing


def _close_cuts(text: str) -> str:
    """Join the text either side of each cut with the stronger separator.

    A deletion that spanned a paragraph boundary keeps the paragraph break; one
    inside a paragraph leaves a single space.
    """

    def join(match: re.Match[str]) -> str:
        return "\n\n" if _BLANK_LINE_RE.search(match.group(0)) else " "

    out = _CUT_RE.sub(join, text)
    out = out.replace(_CUT, "")
    out = _EXCESS_BLANKS_RE.sub("\n\n", out)
    # Tidy a space left dangling before punctuation or at a line end.
    out = re.sub(r" +([.,;:)])", r"\1", out)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return out.strip()


def _rebuild_without(body: str, norm_target: str) -> str:
    """Drop the first whitespace-insensitive occurrence of *norm_target*."""
    norm_chars: list[int] = []
    normalized: list[str] = []
    previous_space = False
    for i, ch in enumerate(body):
        if ch.isspace():
            if previous_space or not normalized:
                continue
            normalized.append(" ")
            norm_chars.append(i)
            previous_space = True
            continue
        normalized.append(ch)
        norm_chars.append(i)
        previous_space = False
    haystack = "".join(normalized).strip()
    offset = len("".join(normalized)) - len("".join(normalized).lstrip())
    start = haystack.find(norm_target)
    if start < 0:
        return body
    lo = norm_chars[start + offset]
    hi_index = start + offset + len(norm_target) - 1
    hi = norm_chars[min(hi_index, len(norm_chars) - 1)]
    return body[:lo] + _CUT + body[hi + 1 :]


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
        # Per-claim record of what the gate did, so a refused narrowing or a
        # hallucinated span is visible in a run's output rather than only in a
        # WARNING nobody reads.
        actions: list[tuple[int, str, str, str]] = []
        for i, issue in enumerate(issues, start=1):
            verdict = by_index.get(i)
            if verdict is None:
                logger.info("no verdict for issue %d (%s); keeping it", i, issue.title)
                kept.append(issue)
                actions.append((i, issue.title, "no-verdict", "kept"))
                continue
            if verdict.verdict == "refuted":
                logger.info("dropping issue %d (%s): %s", i, issue.title, verdict.reasoning[:160])
                actions.append((i, issue.title, verdict.verdict, "dropped"))
                continue
            if verdict.verdict == "partly_supported":
                narrowed, removed, missing = narrow_by_deletion(issue.body, verdict.remove_spans)
                if missing:
                    logger.info(
                        "issue %d (%s): %d named span(s) not found in the body",
                        i,
                        issue.title,
                        len(missing),
                    )
                if not removed:
                    # Nothing could be removed, so there is nothing to narrow
                    # to. Keeping the original is the safe reading: the
                    # reviewer called the issue partly right, so dropping it
                    # would lose a concern it endorsed.
                    logger.info(
                        "issue %d (%s): nothing removable; keeping the original",
                        i,
                        issue.title,
                    )
                    kept.append(issue)
                    actions.append((i, issue.title, verdict.verdict, "kept"))
                    continue
                if len(narrowed) < _MIN_NARROWED_CHARS:
                    # Every substantive sentence was named for removal, which
                    # is a refutation stated as a narrowing.
                    logger.info(
                        "issue %d (%s): narrowing removed the whole concern; dropping it",
                        i,
                        issue.title,
                    )
                    actions.append((i, issue.title, verdict.verdict, "dropped"))
                    continue
                logger.info(
                    "narrowing issue %d (%s): removed %d span(s), %d -> %d chars; %s",
                    i,
                    issue.title,
                    len(removed),
                    len(issue.body),
                    len(narrowed),
                    "; ".join(verdict.removal_reasons)[:200] or "(no reason given)",
                )
                kept.append(issue.model_copy(update={"body": narrowed}))
                actions.append((i, issue.title, verdict.verdict, "narrowed"))
                continue
            kept.append(issue)
            actions.append((i, issue.title, verdict.verdict, "kept"))

        logger.info("issue actions: %s", actions)
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
