"""Role orchestration for the bounded agent runtime (#264).

Two modes, both over the same workspace and tools:

``single``
    One referee with the whole paper and computation, then the editor. This is
    the cheap arm: it tests whether retrieval and computation alone close the
    gap, before paying for the swarm.

``swarm``
    Planner divides the paper into claim-shaped targets; investigators work
    them in parallel; one refuter per candidate finding re-establishes it in a
    fresh context that has never seen the investigator's reasoning; the editor
    writes the report from survivors only.

The refutation step is the part that matters for correctness. The pipeline's
known failure mode is a confident wrong critique that later stages elaborate
rather than check, because each stage inherits the previous one's framing. A
refuter that sees only the claim and the paper cannot inherit the framing, so
its agreement carries information. The agent-swarm literature reports the same
mechanism as the defense against a swarm amplifying its own error: every result
verified by a fresh agent with no shared memory of the work
(arXiv:2609.35719 Section 4.1).
"""

from __future__ import annotations

import datetime
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal

from pydantic import BaseModel, Field

from coarse.agent.runner import run_agent
from coarse.agent.tools import ToolBox, finding_from_payload
from coarse.agent.types import (
    AgentRunRecord,
    FindingBatch,
    InvestigationPlan,
    InvestigationTarget,
    LedgerFinding,
    RefutationVerdict,
)
from coarse.agent.workspace import ReviewWorkspace
from coarse.llm import LLMClient
from coarse.prompts import (
    AGENT_EDITOR_SYSTEM,
    AGENT_INVESTIGATOR_SYSTEM,
    AGENT_PLANNER_SYSTEM,
    AGENT_REFUTER_SYSTEM,
    agent_editor_user,
    agent_investigator_user,
    agent_planner_user,
    agent_refuter_user,
)
from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    Review,
    SectionType,
)

logger = logging.getLogger(__name__)

DEFAULT_MAX_TARGETS = 10
DEFAULT_MAX_PARALLEL = 4
INVESTIGATOR_TOOL_BUDGET = 40
REFUTER_TOOL_BUDGET = 20
PLANNER_TOOL_BUDGET = 35
SINGLE_TOOL_BUDGET = 70

# Labelled objects to surface to the planner. These are the things proofs
# invoke, and the gap between a label's statement and its use is where the
# findings this harness targets actually live.
_LABEL_RE = re.compile(
    r"\b(Theorem|Lemma|Proposition|Corollary|Claim|Definition|Algorithm|Assumption|Remark)"
    # Case-sensitive on purpose. With IGNORECASE the single-letter alternative
    # matched the first letter of an ordinary following word, turning
    # "Assumption that ..." into the label "Assumption t".
    r"\s+(\d+[a-z]?(?:\.\d+)*|[A-Z](?:\.\d+)+|[A-Z](?=[\s.,:)]))",
)


class _AgentReport(BaseModel):
    """Editor submission envelope."""

    assessment: str = Field(default="", description="2-3 sentences on the contribution")
    issues: list[OverviewIssue] = Field(default_factory=list, description="4-6 macro issues")
    recommendation: str = Field(default="", description="accept / minor / major revision / reject")
    revision_targets: list[str] = Field(default_factory=list)
    detailed_comments: list[DetailedComment] = Field(default_factory=list)


def extract_labels(paper_markdown: str, *, limit: int = 160) -> str:
    """List the paper's labelled objects with where each is first stated."""
    seen: dict[str, int] = {}
    for m in _LABEL_RE.finditer(paper_markdown):
        key = f"{m.group(1).capitalize()} {m.group(2)}"
        seen.setdefault(key, m.start())
    if not seen:
        return "(no labelled theorems/lemmas/definitions found)"
    items = sorted(seen.items(), key=lambda kv: kv[1])[:limit]
    return "\n".join(f"- {k} (first at char {v})" for k, v in items)


def _section_text(structure: PaperStructure, *types: SectionType) -> str:
    for sec in structure.sections:
        if sec.section_type in types and sec.text.strip():
            return sec.text
    return ""


def _render_findings_for_editor(
    findings: list[LedgerFinding],
    verdicts: dict[str, RefutationVerdict],
) -> str:
    blocks = []
    for f in findings:
        v = verdicts.get(f.finding_id)
        claim = v.corrected_claim.strip() if v and v.corrected_claim.strip() else f.claim
        severity = v.severity_after_review if v else f.severity
        anchors = "\n".join(f"  QUOTE: {a.quote}" for a in f.anchors) or "  (no anchor recorded)"
        blocks.append(
            f"### Finding {f.finding_id} — {f.title}\n"
            f"Location: {f.location}\n"
            f"Severity: {severity}\n"
            f"Defect: {claim}\n"
            f"Consequence: {f.why_it_matters}\n"
            f"Suggested fix: {f.remediation}\n"
            f"Verbatim anchors (copy a quote from here exactly):\n{anchors}"
        )
    return "\n\n".join(blocks)


def _plan(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    *,
    max_targets: int,
    author_notes: str | None,
    records: list[AgentRunRecord],
) -> list[InvestigationTarget]:
    toolbox = ToolBox(
        workspace=workspace, allow_python=False, allow_write=False, max_calls=PLANNER_TOOL_BUDGET
    )
    result = run_agent(
        client,
        role="planner",
        agent_id="planner",
        system=AGENT_PLANNER_SYSTEM,
        task=agent_planner_user(
            structure.title,
            structure.domain,
            structure.abstract,
            (workspace.root / "outline.md").read_text(encoding="utf-8"),
            extract_labels(workspace.paper_text),
            _section_text(structure, SectionType.INTRODUCTION) or structure.abstract,
            max_targets,
            author_notes=author_notes,
        ),
        toolbox=toolbox,
        submit_model=InvestigationPlan,
        submit_description=(
            "Submit the investigation plan. It must contain at least one target; an "
            "empty plan means no referee is assigned and the paper goes unreviewed."
        ),
        max_turns=14,
        max_tokens=8192,
    )
    records.append(result.record)
    plan = result.result
    targets = list(plan.targets)[:max_targets] if isinstance(plan, InvestigationPlan) else []
    if not targets:
        # The planner can spend its whole tool budget skimming and then submit
        # an empty plan. Falling back to one whole-paper target wastes the
        # parallelism and measurably under-covers the paper, so derive targets
        # from the paper's own structure instead.
        logger.warning(
            "planner produced no targets (%d turns, %d tool calls); "
            "deriving targets from the paper structure",
            result.record.turns,
            result.record.tool_calls,
        )
        targets = _structural_targets(structure, max_targets)
    # Normalize ids so ledger filenames are stable regardless of what the
    # model emitted.
    for i, t in enumerate(targets, start=1):
        t.target_id = f"t{i:02d}"
    return targets


def _structural_targets(
    structure: PaperStructure,
    max_targets: int,
) -> list[InvestigationTarget]:
    """Derive investigation targets deterministically from the paper's sections.

    The fallback when the planner returns nothing. Ranks sections the way
    ``select_reviewable_sections`` does (length, with mathematical content
    weighted up) and asks, for each, the question that the reference findings
    this harness targets are shaped like: does this argument establish what the
    results it invokes require?
    """
    candidates = [
        s for s in structure.sections if s.text.strip() and s.section_type != SectionType.REFERENCES
    ]
    ranked = sorted(
        candidates,
        key=lambda s: -len(s.text) * (2.5 if s.math_content else 1.0),
    )[: max(1, max_targets)]

    targets: list[InvestigationTarget] = []
    for i, section in enumerate(ranked, start=1):
        if section.math_content:
            question = (
                f"Work through the argument in '{section.title}'. Does each step follow, "
                "and does it establish what the definitions, lemmas and algorithms it "
                "invokes actually require? Look each of them up and compare."
            )
        else:
            question = (
                f"Check '{section.title}' against the paper's formal results. Are the "
                "claims it makes supported by what is actually proved, and do the "
                "parameter values it uses satisfy the conditions the theory requires?"
            )
        targets.append(
            InvestigationTarget(
                target_id=f"t{i:02d}",
                question=question,
                locations=[section.title],
                rationale="Derived from the paper structure because no plan was produced.",
            )
        )
    return targets


def _whole_paper_target() -> InvestigationTarget:
    return InvestigationTarget(
        target_id="t01",
        question=(
            "Review this paper as a referee: check its central results against their "
            "proofs, its theoretical requirements against what the experiments do, and "
            "its appendices against the main text."
        ),
        locations=["the whole paper, including every appendix"],
        rationale="No plan was produced; fall back to a single broad pass.",
    )


def _investigate(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    target: InvestigationTarget,
    *,
    author_notes: str | None,
    tool_budget: int,
    max_turns: int,
) -> tuple[list[LedgerFinding], AgentRunRecord]:
    toolbox = ToolBox(workspace=workspace, max_calls=tool_budget)
    result = run_agent(
        client,
        role="investigator",
        agent_id=target.target_id,
        system=AGENT_INVESTIGATOR_SYSTEM,
        task=agent_investigator_user(
            structure.title,
            target.question,
            "\n".join(f"- {loc}" for loc in target.locations) or "- (not specified)",
            target.rationale,
            author_notes=author_notes,
        ),
        toolbox=toolbox,
        submit_model=FindingBatch,
        submit_description=(
            "Submit your findings for this target. An empty list is a valid and "
            "preferred result when nothing is demonstrable."
        ),
        max_turns=max_turns,
        max_tokens=16384,
    )
    findings: list[LedgerFinding] = []
    if isinstance(result.result, FindingBatch):
        for i, f in enumerate(result.result.findings, start=1):
            try:
                findings.append(
                    finding_from_payload(f.model_dump(), target_id=target.target_id, index=i)
                )
            except Exception:
                logger.debug("dropping malformed finding from %s", target.target_id, exc_info=True)
    return findings, result.record


def _refute(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    finding: LedgerFinding,
) -> tuple[RefutationVerdict | None, AgentRunRecord]:
    """Re-establish one finding in a context that has not seen how it was made.

    The prompt carries the claim, its location and the paper passages it points
    at. It deliberately does not carry the investigator's reasoning or its
    computation transcript: a refuter shown the derivation tends to audit the
    derivation rather than the paper, which is the failure this step exists to
    prevent.
    """
    toolbox = ToolBox(workspace=workspace, max_calls=REFUTER_TOOL_BUDGET)
    anchors = "\n\n".join(a.quote for a in finding.anchors) or "(none recorded)"
    result = run_agent(
        client,
        role="refuter",
        agent_id=f"ref-{finding.finding_id}",
        system=AGENT_REFUTER_SYSTEM,
        task=agent_refuter_user(structure.title, finding.claim, finding.location, anchors),
        toolbox=toolbox,
        submit_model=RefutationVerdict,
        submit_description="Submit your verdict on this one criticism.",
        max_turns=12,
        max_tokens=8192,
    )
    verdict = result.result if isinstance(result.result, RefutationVerdict) else None
    if verdict is not None:
        verdict.finding_id = finding.finding_id
    return verdict, result.record


def _edit(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    findings: list[LedgerFinding],
    verdicts: dict[str, RefutationVerdict],
    *,
    author_notes: str | None,
    language: str | None,
    records: list[AgentRunRecord],
) -> _AgentReport | None:
    toolbox = ToolBox(workspace=workspace, allow_python=False, allow_write=False, max_calls=12)
    result = run_agent(
        client,
        role="editor",
        agent_id="editor",
        system=AGENT_EDITOR_SYSTEM,
        task=agent_editor_user(
            structure.title,
            structure.domain,
            structure.abstract,
            _render_findings_for_editor(findings, verdicts),
            author_notes=author_notes,
            language=language,
        ),
        toolbox=toolbox,
        submit_model=_AgentReport,
        submit_description="Submit the assembled referee report.",
        max_turns=10,
        max_tokens=16384,
    )
    records.append(result.record)
    return result.result if isinstance(result.result, _AgentReport) else None


def _fallback_report(
    findings: list[LedgerFinding],
    verdicts: dict[str, RefutationVerdict],
) -> _AgentReport:
    """Render the ledger directly when the editor fails.

    Deterministic, so a failed editor degrades to a plainer report rather than
    discarding findings that were already checked.
    """
    severity_rank = {"critical": 0, "major": 1, "minor": 2}
    ordered = sorted(
        findings,
        key=lambda f: severity_rank.get(
            (
                verdicts[f.finding_id].severity_after_review
                if f.finding_id in verdicts
                else f.severity
            ),
            1,
        ),
    )
    comments: list[DetailedComment] = []
    for i, f in enumerate(ordered, start=1):
        v = verdicts.get(f.finding_id)
        claim = v.corrected_claim.strip() if v and v.corrected_claim.strip() else f.claim
        quote = next((a.quote for a in f.anchors if len(a.quote) >= 20), "")
        if not quote:
            continue
        body = claim if not f.remediation else f"{claim}\n\n{f.remediation}"
        comments.append(
            DetailedComment(
                number=i,
                title=f.title,
                quote=quote,
                feedback=body,
                severity=(v.severity_after_review if v else f.severity),
                confidence="high",
            )
        )
    return _AgentReport(
        assessment="",
        issues=[OverviewIssue(title=f.title, body=f.claim) for f in ordered[:6]]
        or [OverviewIssue(title="No issues confirmed", body="No finding survived review.")],
        detailed_comments=comments,
    )


def run_agentic_review(
    paper_markdown: str,
    structure: PaperStructure,
    client: LLMClient,
    *,
    mode: Literal["single", "swarm"] = "swarm",
    max_targets: int = DEFAULT_MAX_TARGETS,
    max_parallel: int = DEFAULT_MAX_PARALLEL,
    author_notes: str | None = None,
    language: str | None = None,
    workspace_root: str | None = None,
    keep_workspace: bool = False,
) -> tuple[Review, list[AgentRunRecord], ReviewWorkspace]:
    """Run an agentic review and return the Review plus per-agent accounting.

    The caller owns quote verification and rendering: this returns a ``Review``
    whose comments still have to pass ``quote_verify``, exactly like the
    pipeline's own stages, so the verbatim-quote guarantee is unchanged.

    The workspace is returned so the caller can inspect the ledger; it is
    deleted on cleanup unless ``keep_workspace`` is set.
    """
    records: list[AgentRunRecord] = []
    workspace = ReviewWorkspace.create(
        paper_markdown,
        structure,
        root=workspace_root,  # type: ignore[arg-type]
    )
    if keep_workspace:
        workspace._owns_root = False  # noqa: SLF001 - caller asked to keep it

    if mode == "single":
        targets = [_whole_paper_target()]
    else:
        targets = _plan(
            client,
            workspace,
            structure,
            max_targets=max_targets,
            author_notes=author_notes,
            records=records,
        )
    logger.info("agentic review: %d target(s) in %s mode", len(targets), mode)

    # --- investigate -----------------------------------------------------
    findings: list[LedgerFinding] = []
    budget = SINGLE_TOOL_BUDGET if mode == "single" else INVESTIGATOR_TOOL_BUDGET
    turns = 40 if mode == "single" else 24
    with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(targets)))) as pool:
        futures = {
            pool.submit(
                _investigate,
                client,
                workspace,
                structure,
                t,
                author_notes=author_notes,
                tool_budget=budget,
                max_turns=turns,
            ): t
            for t in targets
        }
        for fut in as_completed(futures):
            target = futures[fut]
            try:
                got, record = fut.result()
            except Exception:
                logger.warning("investigator %s failed", target.target_id, exc_info=True)
                continue
            records.append(record)
            for f in got:
                workspace.write_finding(f)
            findings.extend(got)

    logger.info("agentic review: %d candidate finding(s)", len(findings))

    # --- refute ----------------------------------------------------------
    verdicts: dict[str, RefutationVerdict] = {}
    if mode == "swarm" and findings:
        with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(findings)))) as pool:
            futures = {pool.submit(_refute, client, workspace, structure, f): f for f in findings}
            for fut in as_completed(futures):
                finding = futures[fut]
                try:
                    verdict, record = fut.result()
                except Exception:
                    logger.warning("refuter for %s failed", finding.finding_id, exc_info=True)
                    continue
                records.append(record)
                if verdict is not None:
                    verdicts[verdict.finding_id] = verdict
                    workspace.write_verdict(verdict)

        confirmed = [
            f
            for f in findings
            if verdicts.get(f.finding_id, None) and verdicts[f.finding_id].verdict == "confirmed"
        ]
        logger.info(
            "agentic review: %d/%d finding(s) confirmed on independent review",
            len(confirmed),
            len(findings),
        )
    else:
        confirmed = findings

    # --- edit ------------------------------------------------------------
    report = _edit(
        client,
        workspace,
        structure,
        confirmed,
        verdicts,
        author_notes=author_notes,
        language=language,
        records=records,
    )
    if report is None:
        logger.warning("editor failed; rendering the ledger directly")
        report = _fallback_report(confirmed, verdicts)

    issues = report.issues or [
        OverviewIssue(
            title="No issues confirmed",
            body=(
                "No candidate finding survived independent review. The paper may be "
                "sound in the respects checked, or the review may have been too narrow."
            ),
        )
    ]
    overview = OverviewFeedback(
        assessment=report.assessment,
        issues=issues,
        recommendation=report.recommendation,
        revision_targets=report.revision_targets,
    )
    comments = [
        c.model_copy(update={"number": i}) for i, c in enumerate(report.detailed_comments, start=1)
    ]
    review = Review(
        title=structure.title,
        domain=structure.domain,
        taxonomy=structure.taxonomy,
        date=datetime.date.today().strftime("%m/%d/%Y"),
        overall_feedback=overview,
        detailed_comments=comments,
    )
    workspace.dump_manifest(
        {
            "mode": mode,
            "model": client.model,
            "targets": [t.model_dump() for t in targets],
            "candidate_findings": len(findings),
            "confirmed_findings": len(confirmed),
            "verdicts": {k: v.verdict for k, v in verdicts.items()},
            "agents": [r.model_dump() for r in records],
            "cost_usd": sum(r.cost_usd for r in records),
        }
    )
    return review, records, workspace
