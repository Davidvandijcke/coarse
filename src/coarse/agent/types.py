"""Typed records for the bounded agent runtime (#264).

Every candidate finding an investigator produces becomes a ``LedgerFinding``
on disk. A refuter running in a fresh context writes a ``RefutationVerdict``
beside it. The editor may only draw on findings whose verdict is
``confirmed``, which is what stops a confident-but-wrong claim from reaching
the user on the strength of agreement between agents that shared context.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PaperAnchor(BaseModel):
    """A located passage in the extracted paper."""

    section_id: str = Field(description="Section file stem, e.g. '036-a-10-proof-of-proposition-2'")
    section_title: str = Field(default="", description="Human-readable section heading")
    char_start: int = Field(default=0, description="Character offset into paper.md")
    quote: str = Field(description="Verbatim text from the paper at this anchor")


class InvestigationTarget(BaseModel):
    """One claim-shaped unit of work handed to an investigator.

    Deliberately not section-shaped: the reference findings this harness is
    built to recover are overwhelmingly of the form "the proof in A.10 does
    not establish what Definition 2 requires", which spans two locations.
    """

    target_id: str = Field(description="Short stable id, e.g. 't03'")
    question: str = Field(
        description="The specific thing to check, phrased so it can come back negative"
    )
    locations: list[str] = Field(
        default_factory=list,
        description="Section titles or labels (theorem/lemma/appendix numbers) that bear on it",
    )
    rationale: str = Field(
        default="",
        description="Why this is worth an investigator's time",
    )


class InvestigationPlan(BaseModel):
    """Planner output.

    At least one target is required. Unlike ``FindingBatch``, where an empty
    result is the correct answer when nothing is wrong, an empty plan is never
    useful: it means no referee is assigned. Leaving the list optional let the
    planner submit ``{"targets": []}`` after a few turns of reading — it did so
    on every run — which silently handed the whole paper to one fallback
    investigation. Requiring a target makes that submission fail validation, so
    the runner feeds the error back and the planner tries again.
    """

    targets: list[InvestigationTarget] = Field(
        min_length=1,
        description="One or more investigation targets, ordered most promising first.",
    )


class LedgerFinding(BaseModel):
    """A candidate finding with its evidence, as written to findings/<id>.json."""

    finding_id: str = Field(description="Stable id, e.g. 't03-f1'")
    target_id: str = Field(default="", description="Investigation target that produced it")
    title: str = Field(description="Short title")
    location: str = Field(default="", description="Where in the paper the problem is")
    claim: str = Field(
        description="The defect, stated so that it is checkable and could be shown false"
    )
    why_it_matters: str = Field(
        default="",
        description="What breaks downstream if the claim holds",
    )
    remediation: str = Field(default="", description="What the authors could do about it")
    anchors: list[PaperAnchor] = Field(
        default_factory=list,
        description="Verbatim passages the claim rests on",
    )
    computation: str = Field(
        default="",
        description="Transcript of any algebra or numeric check that was run",
    )
    severity: Literal["critical", "major", "minor"] = Field(default="major")
    self_confidence: Literal["high", "medium", "low"] = Field(default="medium")


class FindingBatch(BaseModel):
    """Investigator output envelope. Empty is a valid, preferred result when
    nothing substantive was found (see #260 on abstention)."""

    findings: list[LedgerFinding] = Field(default_factory=list)


class RefutationVerdict(BaseModel):
    """Fresh-context verdict on a single candidate finding.

    ``confirmed`` requires the refuter to have independently reproduced the
    defect from the paper, not merely to have found the claim plausible.
    """

    finding_id: str = Field(description="The finding being judged")
    verdict: Literal["confirmed", "refuted", "inconclusive"] = Field(
        description=(
            "confirmed: independently reproduced from the paper. "
            "refuted: the paper does not have this defect, or the claim "
            "misreads it. inconclusive: could not settle it either way."
        )
    )
    reasoning: str = Field(description="How the verdict was reached, citing the paper")
    corrected_claim: str = Field(
        default="",
        description=(
            "If the finding is real but misstated, the accurate version. "
            "Empty when the original claim stands as written."
        ),
    )
    severity_after_review: Literal["critical", "major", "minor"] = Field(default="major")


class AgentRunRecord(BaseModel):
    """Per-agent accounting, for the run manifest (#273)."""

    role: str
    agent_id: str
    model: str
    tool_calls: int = 0
    turns: int = 0
    cost_usd: float = 0.0
    duration_s: float = 0.0
    error: str = ""
