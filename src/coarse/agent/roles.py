"""The agents each role runs, as single calls into the tool loop.

Split from ``orchestrator``, which sequences them. Keeping the two apart
matters for one of them in particular: ``_refute`` is deliberately given the
claim and the paper and *not* the investigator's reasoning, and that omission
is easier to see and harder to undo when the function is not buried in the
flow that produced the claim.
"""

from __future__ import annotations

import logging

from coarse.agent.runner import run_agent
from coarse.agent.tools import ToolBox, finding_from_payload
from coarse.agent.types import (
    AgentRunRecord,
    FindingBatch,
    InvestigationTarget,
    LedgerFinding,
    RefutationVerdict,
)
from coarse.agent.workspace import ReviewWorkspace
from coarse.llm import LLMClient
from coarse.prompts import (
    AGENT_INVESTIGATOR_SYSTEM,
    AGENT_REFUTER_SYSTEM,
    AGENT_ROUND2_SYSTEM,
    AGENT_SWEEP_SYSTEM,
    agent_investigator_user,
    agent_refuter_user,
    agent_round2_user,
    agent_sweep_user,
)
from coarse.types import PaperStructure

logger = logging.getLogger(__name__)

#: Tool-call budgets per role. An investigator reads whole appendices and
#: computes; a refuter checks one claim.
INVESTIGATOR_TOOL_BUDGET = 40
REFUTER_TOOL_BUDGET = 20
SINGLE_TOOL_BUDGET = 70


def _investigate(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    target: InvestigationTarget,
    *,
    author_notes: str | None,
    tool_budget: int,
    max_turns: int,
    breadth: bool = False,
) -> tuple[list[LedgerFinding], AgentRunRecord]:
    toolbox = ToolBox(workspace=workspace, max_calls=tool_budget)
    if breadth:
        system = AGENT_SWEEP_SYSTEM
        task = agent_sweep_user(
            structure.title,
            target.question,
            target.rationale,
            author_notes=author_notes,
        )
    else:
        system = AGENT_INVESTIGATOR_SYSTEM
        task = agent_investigator_user(
            structure.title,
            target.question,
            "\n".join(f"- {loc}" for loc in target.locations) or "- (not specified)",
            target.rationale,
            author_notes=author_notes,
        )
    result = run_agent(
        client,
        role="sweep" if breadth else "investigator",
        agent_id=target.target_id,
        system=system,
        task=task,
        toolbox=toolbox,
        submit_model=FindingBatch,
        submit_description=(
            "Submit your findings for this target. An empty list is valid when "
            "nothing is demonstrable."
            if breadth
            else "Submit your findings for this target. An empty list is a valid and "
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


def _cross_reference(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    target: InvestigationTarget,
    own_findings: list[LedgerFinding],
    *,
    author_notes: str | None,
) -> tuple[list[LedgerFinding], AgentRunRecord]:
    """Re-run one investigator with the shared board of others' findings.

    Addresses the swarm's measured deficiency, which is coverage rather than
    precision. Its investigators work in isolation, so one checking an
    appendix proof never learns that another found the same quantity treated
    differently in the main text — the exact shape of the cross-location
    findings this harness exists to recover.

    The board carries titles, locations and one-line claims and nothing of the
    reasoning behind them, and the brief forbids repeating or relying on an
    entry. Anything this round produces still goes through the independent
    refuter, so a lead that spreads without being demonstrated does not
    survive.
    """
    toolbox = ToolBox(workspace=workspace, max_calls=INVESTIGATOR_TOOL_BUDGET)
    already = (
        "\n".join(f"- {f.title}: {' '.join(f.claim.split())[:200]}" for f in own_findings)
        or "(nothing)"
    )
    board = (
        workspace.board_path.read_text(encoding="utf-8")
        if workspace.board_path.is_file()
        else "(no board)"
    )
    result = run_agent(
        client,
        role="cross_reference",
        agent_id=f"x-{target.target_id}",
        system=AGENT_ROUND2_SYSTEM,
        task=agent_round2_user(
            structure.title,
            target.question,
            "\n".join(f"- {loc}" for loc in target.locations) or "- (not specified)",
            board,
            already,
            author_notes=author_notes,
        ),
        toolbox=toolbox,
        submit_model=FindingBatch,
        submit_description=(
            "Submit any NEW defect in your own part of the paper that the other "
            "referees' leads led you to and that you demonstrated yourself. An empty "
            "list is the expected outcome for most sections."
        ),
        max_turns=20,
        max_tokens=16384,
    )
    findings: list[LedgerFinding] = []
    if isinstance(result.result, FindingBatch):
        for i, f in enumerate(result.result.findings, start=1):
            try:
                findings.append(
                    finding_from_payload(f.model_dump(), target_id=f"{target.target_id}x", index=i)
                )
            except Exception:
                logger.debug("dropping malformed round-2 finding", exc_info=True)
    return findings, result.record


def _refute(
    client: LLMClient,
    workspace: ReviewWorkspace,
    structure: PaperStructure,
    finding: LedgerFinding,
    language: str | None = None,
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
        task=agent_refuter_user(
            structure.title, finding.claim, finding.location, anchors, language=language
        ),
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
