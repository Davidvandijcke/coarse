"""Apply the refutation gate to comments produced outside the agent roles.

The gate in ``orchestrator`` guards findings an investigator produced. This
module applies the same gate to a review the staged pipeline already produced,
which is what ``review_paper(refute=True)`` and ``coarse review --refute`` use.

It is separate because the measurement made it the primary use. Generation and
verification turned out to be complements rather than substitutes: the staged
pipeline led on coverage on both benchmark papers and also asserted the most
claims the paper does not support, while the agent-only arms reversed both. So
the gate earns its keep applied to the pipeline's output rather than replacing
it. See docs/AGENTIC_REVIEW.md for the per-claim measurement.

Comments only. The same gate was built for the macro issues and measured on
three papers, and it did not earn its place: it converted no unsupported issue
on one paper while dropping a supported one, its whole upside on the other was
two re-judgements by a judge known to change verdict on identical text, and
reading the narrowed output found an issue whose title still asserted a defect
its own narrowed body now said did not exist. That work is in the branch
history (``refute_issues`` and ``narrow_by_deletion``, removed in the commit
that references this note) if it is ever worth revisiting with more papers.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from coarse.agent.orchestrator import DEFAULT_MAX_PARALLEL, _refute
from coarse.agent.types import (
    AgentRunRecord,
    LedgerFinding,
    PaperAnchor,
    RefutationVerdict,
)
from coarse.agent.workspace import ReviewWorkspace
from coarse.llm import LLMClient
from coarse.types import DetailedComment, PaperStructure

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
