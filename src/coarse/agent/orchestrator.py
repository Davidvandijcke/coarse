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

from coarse.agent.roles import (
    INVESTIGATOR_TOOL_BUDGET,
    SINGLE_TOOL_BUDGET,
    _cross_reference,
    _investigate,
    _refute,
)
from coarse.agent.runner import run_agent
from coarse.agent.tools import ToolBox
from coarse.agent.types import (
    AgentRunRecord,
    InvestigationPlan,
    InvestigationTarget,
    LedgerFinding,
    RefutationVerdict,
)
from coarse.agent.workspace import ReviewWorkspace
from coarse.llm import LLMClient
from coarse.prompts import (
    AGENT_EDITOR_SYSTEM,
    AGENT_PLANNER_SYSTEM,
    agent_editor_user,
    agent_planner_user,
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

#: The modes ``run_agentic_review`` accepts. Validated rather than falling
#: through to "swarm", so a typo in ``--agent`` is an error the user sees
#: instead of a silent substitution of a different, dearer mode.
AGENT_MODES = frozenset({"single", "swarm", "sweep"})

DEFAULT_MAX_TARGETS = 10
DEFAULT_MAX_PARALLEL = 4
PLANNER_TOOL_BUDGET = 35

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


class _EditorComment(DetailedComment):
    """A detailed comment the editor must attribute to a ledger finding.

    The editor is told to write only from confirmed findings. Requiring the
    finding id makes that checkable instead of merely instructed: a comment
    whose id is not in the confirmed set is dropped in
    ``_link_comments_to_ledger``, so a finding an independent refuter did not
    reproduce cannot re-enter the report through the editor.
    """

    finding_id: str = Field(
        default="",
        description=(
            "The id of the confirmed finding this comment reports, exactly as given "
            "in the findings list (for example 't03-f1')."
        ),
    )


def _link_comments_to_ledger(
    comments: list[_EditorComment],
    confirmed_ids: set[str],
) -> tuple[list[DetailedComment], list[str]]:
    """Keep only comments attributed to a confirmed finding.

    Returns the kept comments and the titles of the dropped ones. When the
    editor attributes nothing at all (an older or confused model returning no
    ids), the comments are kept: the alternative is discarding a whole report
    over a missing field, and the prompt-level constraint still applies. That
    degradation is logged so it is visible in a run's output.
    """
    if not any(c.finding_id.strip() for c in comments):
        logger.warning(
            "editor attributed no comment to a ledger finding; keeping all %d "
            "comments on the prompt-level constraint alone",
            len(comments),
        )
        return [DetailedComment.model_validate(c.model_dump()) for c in comments], []

    kept: list[DetailedComment] = []
    dropped: list[str] = []
    for comment in comments:
        if comment.finding_id.strip() in confirmed_ids:
            kept.append(DetailedComment.model_validate(comment.model_dump()))
        else:
            dropped.append(f"{comment.title} (finding_id={comment.finding_id!r})")
    if dropped:
        logger.warning(
            "dropping %d editor comment(s) not attributed to a confirmed finding: %s",
            len(dropped),
            "; ".join(dropped),
        )
    return kept, dropped


class _AgentReport(BaseModel):
    """Editor submission envelope."""

    assessment: str = Field(default="", description="2-3 sentences on the contribution")
    issues: list[OverviewIssue] = Field(default_factory=list, description="4-6 macro issues")
    recommendation: str = Field(default="", description="accept / minor / major revision / reject")
    revision_targets: list[str] = Field(default_factory=list)
    detailed_comments: list[_EditorComment] = Field(default_factory=list)


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


def _sweep_targets(
    structure: PaperStructure,
    workspace: ReviewWorkspace,
    max_targets: int,
) -> list[InvestigationTarget]:
    """Divide the whole paper into contiguous regions, one per investigator.

    Where ``_structural_targets`` picks the most promising sections and asks one
    question each, this covers every reviewable section. The arm it serves
    exists because the two capabilities measured separately were complementary:
    a single full-paper pass had the breadth and the role swarm had the
    precision, so this gives a broad pass the swarm's refutation step.
    """
    sections = [s for s in structure.sections if s.text.strip()]
    if not sections:
        return [_whole_paper_target()]
    groups = max(1, min(max_targets, len(sections)))
    per_group = -(-len(sections) // groups)
    id_by_title = {s.title: s.section_id for s in workspace.sections}

    targets: list[InvestigationTarget] = []
    for i in range(0, len(sections), per_group):
        chunk = sections[i : i + per_group]
        listing = "\n".join(
            f"- `{id_by_title.get(s.title, '?')}` {s.title} "
            f"({len(s.text)} chars{', mathematical' if s.math_content else ''})"
            for s in chunk
        )
        region = f"{chunk[0].title} through {chunk[-1].title}"
        targets.append(
            InvestigationTarget(
                target_id=f"t{len(targets) + 1:02d}",
                question=region,
                locations=[s.title for s in chunk],
                rationale=listing,
            )
        )
    return targets


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
            _EditorComment(
                number=i,
                title=f.title,
                quote=quote,
                feedback=body,
                severity=(v.severity_after_review if v else f.severity),
                confidence="high",
                finding_id=f.finding_id,
            )
        )
    return _AgentReport(
        assessment="",
        issues=[OverviewIssue(title=f.title, body=f.claim) for f in ordered[:6]]
        or [OverviewIssue(title="No issues confirmed", body="No finding survived review.")],
        detailed_comments=comments,
    )


def _refute_all(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    findings: list[LedgerFinding],
    *,
    max_parallel: int,
    records: list[AgentRunRecord],
) -> tuple[dict[str, RefutationVerdict], list[LedgerFinding]]:
    """Refute a batch of candidate findings; return verdicts and survivors."""
    verdicts: dict[str, RefutationVerdict] = {}
    if not findings:
        return verdicts, []
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
        if verdicts.get(f.finding_id) and verdicts[f.finding_id].verdict == "confirmed"
    ]
    logger.info(
        "refutation: %d/%d finding(s) confirmed on independent review",
        len(confirmed),
        len(findings),
    )
    return verdicts, confirmed


def _assemble(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    confirmed: list[LedgerFinding],
    verdicts: dict[str, RefutationVerdict],
    *,
    author_notes: str | None,
    language: str | None,
    records: list[AgentRunRecord],
) -> tuple[Review, list[str]]:
    """Run the editor over confirmed findings and build the Review."""
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
    linked, unlinked = _link_comments_to_ledger(
        report.detailed_comments, {f.finding_id for f in confirmed}
    )
    comments = [c.model_copy(update={"number": i}) for i, c in enumerate(linked, start=1)]
    review = Review(
        title=structure.title,
        domain=structure.domain,
        taxonomy=structure.taxonomy,
        date=datetime.date.today().strftime("%m/%d/%Y"),
        overall_feedback=overview,
        detailed_comments=comments,
    )
    return review, unlinked


def run_agentic_review(
    paper_markdown: str,
    structure: PaperStructure,
    client: LLMClient,
    *,
    mode: Literal["single", "swarm", "sweep"] = "swarm",
    max_targets: int = DEFAULT_MAX_TARGETS,
    max_parallel: int = DEFAULT_MAX_PARALLEL,
    author_notes: str | None = None,
    language: str | None = None,
    workspace_root: str | None = None,
    keep_workspace: bool = False,
    rounds: int = 1,
    emit_round1_review: bool = False,
) -> tuple[Review, list[AgentRunRecord], ReviewWorkspace]:
    """Run an agentic review and return the Review plus per-agent accounting.

    The caller owns quote verification and rendering: this returns a ``Review``
    whose comments still have to pass ``quote_verify``, exactly like the
    pipeline's own stages, so the verbatim-quote guarantee is unchanged.

    The workspace is returned so the caller can inspect the ledger; it is
    deleted on cleanup unless ``keep_workspace`` is set.

    ``emit_round1_review`` additionally writes ``review_round1.json`` into the
    workspace: the review the first pass alone would have produced, so one
    ``rounds=2`` run yields a matched pair for the A/B in
    ``evals/PREREGISTRATION_xref.md``. It costs one extra editor call.

    ``rounds=2`` adds a cross-reference round in "swarm" and "sweep" mode:
    after the first pass, a digest of every candidate finding is written to the
    workspace and each investigator is re-run with it, to catch defects that
    span its own part of the paper and someone else's. ``rounds=1`` is the
    default and leaves that path untouched.
    """
    if mode not in AGENT_MODES:
        raise ValueError(
            f"unknown agent mode {mode!r}; expected one of {', '.join(sorted(AGENT_MODES))}"
        )
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
    elif mode == "sweep":
        targets = _sweep_targets(structure, workspace, max_targets)
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
    breadth = mode == "sweep"
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
                breadth=breadth,
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

    # --- refute round 1, then assemble arm A -----------------------------
    #
    # The cross-reference round is an increment on the first pass, so one run
    # can emit both arms: the review the first pass alone would have produced,
    # and the review with the second round's findings added. Both then share
    # one plan, one first pass and one set of round-1 verdicts, which removes
    # the planner variance that dominates an unpaired comparison. Round-1
    # findings are refuted once and the verdicts are reused, so the pairing
    # costs one extra editor call and nothing else.
    # See evals/PREREGISTRATION_xref.md.
    verdicts: dict[str, RefutationVerdict] = {}
    confirmed: list[LedgerFinding] = findings
    round1_review: Review | None = None
    gated = mode in {"swarm", "sweep"}

    if gated:
        verdicts, confirmed = _refute_all(
            client, workspace, structure, findings, max_parallel=max_parallel, records=records
        )

    if rounds > 1 and gated and emit_round1_review:
        round1_review, _unlinked1 = _assemble(
            client,
            workspace,
            structure,
            confirmed,
            verdicts,
            author_notes=author_notes,
            language=language,
            records=records,
        )

    # --- cross-reference round -------------------------------------------
    round2: list[LedgerFinding] = []
    if rounds > 1 and gated and findings:
        workspace.write_board([(f.finding_id, f.title, f.location, f.claim) for f in findings])
        by_target = {
            t.target_id: [f for f in findings if f.target_id == t.target_id] for t in targets
        }
        with ThreadPoolExecutor(max_workers=max(1, min(max_parallel, len(targets)))) as pool:
            futures = {
                pool.submit(
                    _cross_reference,
                    client,
                    workspace,
                    structure,
                    t,
                    by_target.get(t.target_id, []),
                    author_notes=author_notes,
                ): t
                for t in targets
            }
            for fut in as_completed(futures):
                target = futures[fut]
                try:
                    got, record = fut.result()
                except Exception:
                    logger.warning("cross-reference %s failed", target.target_id, exc_info=True)
                    continue
                records.append(record)
                for f in got:
                    workspace.write_finding(f)
                round2.extend(got)
        logger.info("cross-reference round: %d additional candidate finding(s)", len(round2))
        findings.extend(round2)

        verdicts2, confirmed2 = _refute_all(
            client, workspace, structure, round2, max_parallel=max_parallel, records=records
        )
        verdicts.update(verdicts2)
        confirmed = confirmed + confirmed2

    # --- edit ------------------------------------------------------------
    review, unlinked = _assemble(
        client,
        workspace,
        structure,
        confirmed,
        verdicts,
        author_notes=author_notes,
        language=language,
        records=records,
    )

    if round1_review is not None:
        (workspace.root / "review_round1.json").write_text(
            round1_review.model_dump_json(indent=1), encoding="utf-8"
        )

    workspace.dump_manifest(
        {
            "mode": mode,
            "model": client.model,
            "targets": [t.model_dump() for t in targets],
            "rounds": rounds,
            "round2_candidate_findings": len(round2),
            "paired_round1_review": round1_review is not None,
            "candidate_findings": len(findings),
            "confirmed_findings": len(confirmed),
            "verdicts": {k: v.verdict for k, v in verdicts.items()},
            "comments_dropped_unlinked": unlinked,
            "agents": [r.model_dump() for r in records],
            "cost_usd": sum(r.cost_usd for r in records),
        }
    )
    return review, records, workspace
