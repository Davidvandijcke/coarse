"""Apply the refutation gate to comments produced outside the agent roles.

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

from coarse.agent.orchestrator import DEFAULT_MAX_PARALLEL, _refute
from coarse.agent.types import AgentRunRecord, LedgerFinding, PaperAnchor, RefutationVerdict
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
) -> tuple[list[DetailedComment], list[RefutationVerdict], list[AgentRunRecord]]:
    """Re-establish each comment of an existing review, dropping what fails.

    This is the refutation gate applied to comments the staged pipeline already
    produced, rather than to findings an investigator produced. It exists
    because of how the arms actually measured: the staged pipeline was the
    recall leader on both benchmark papers and also asserted the most claims
    the paper does not support (roughly half of them), while the agent arms
    reversed both. Generation and verification are therefore better combined
    than substituted.

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
        as_findings = [
            LedgerFinding(
                finding_id=f"c{c.number:03d}",
                title=c.title,
                location="",
                claim=c.feedback,
                severity=c.severity,
                anchors=[PaperAnchor(section_id="", quote=c.quote)],
            )
            for c in comments
        ]
        by_id = {f.finding_id: c for f, c in zip(as_findings, comments, strict=True)}

        with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(as_findings)))) as pool:
            futures = {
                pool.submit(_refute, client, workspace, structure, f): f for f in as_findings
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
                logger.info("no verdict for comment %d; keeping it", comment.number)
                kept.append(comment)
                continue
            if verdict.verdict != "confirmed":
                logger.info(
                    "dropping comment %d (%s): %s",
                    comment.number,
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
