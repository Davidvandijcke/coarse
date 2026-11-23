"""Run one evaluation arm on one paper and save the Review as JSON.

Arms, all on the same model and the same extracted markdown so the comparison
isolates the harness rather than the model or the extraction (#270):

``baseline``     one full-paper prompt, no harness
``pipeline``     the current pipeline, unchanged
``agent_single`` one referee with the workspace, retrieval and computation
``agent_swarm``  planner / investigators / fresh-context refuters / editor

Usage:
    OPENROUTER_API_KEY=... uv run python evals/run_arm.py \
        --paper evals/papers/psi --arm agent_swarm --model openrouter/... --run 1
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import time
from pathlib import Path

from pydantic import BaseModel, Field

from coarse.config import load_config
from coarse.llm import LLMClient
from coarse.quote_verify import verify_quotes
from coarse.synthesis import render_review
from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    Review,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_arm")


class _BaselineReport(BaseModel):
    """Response shape for the no-harness arm."""

    assessment: str = Field(default="")
    issues: list[OverviewIssue] = Field(default_factory=list)
    recommendation: str = Field(default="")
    detailed_comments: list[DetailedComment] = Field(default_factory=list)


_BASELINE_SYSTEM = """\
You are an expert referee for a top journal in the paper's field. Produce a referee \
report on the paper given to you.

Report only defects you can demonstrate: a step that does not follow, a condition that \
is not met, a constant or sign that is wrong, a claim the evidence does not support, an \
experiment that does not test what the theory requires. Reporting nothing is better than \
reporting something you cannot support. There is no quota.

Read the appendices. Proofs are where errors survive.

Every detailed comment must carry a quote copied verbatim from the paper, including its \
LaTeX, exactly as it appears. Order comments by severity, most serious first. Give four \
to six macro-level issues and as many detailed comments as you can genuinely support.
"""


def _load(paper_dir: Path) -> tuple[str, PaperStructure]:
    markdown = (paper_dir / "paper.md").read_text(encoding="utf-8")
    structure = PaperStructure.model_validate_json(
        (paper_dir / "structure.json").read_text(encoding="utf-8")
    )
    return markdown, structure


def _finalize(
    review: Review,
    markdown: str,
    *,
    drop_unverified: bool = True,
) -> tuple[Review, int, int]:
    """Run the production quote verifier, as every pipeline stage does."""
    before = len(review.detailed_comments)
    kept = verify_quotes(review.detailed_comments, markdown, drop_unverified=drop_unverified)
    renumbered = [c.model_copy(update={"number": i}) for i, c in enumerate(kept, start=1)]
    return review.model_copy(update={"detailed_comments": renumbered}), before, len(renumbered)


def run_baseline(markdown: str, structure: PaperStructure, client: LLMClient) -> Review:
    report = client.complete(
        [
            {"role": "system", "content": _BASELINE_SYSTEM},
            {
                "role": "user",
                "content": (
                    f'Review the following paper: "{structure.title}".\n\n'
                    f"<paper_content>\n{markdown}\n</paper_content>"
                ),
            },
        ],
        _BaselineReport,
        max_tokens=32768,
        temperature=0.2,
    )
    return Review(
        title=structure.title,
        domain=structure.domain,
        taxonomy=structure.taxonomy,
        date=datetime.date.today().strftime("%m/%d/%Y"),
        overall_feedback=OverviewFeedback(
            assessment=report.assessment,
            issues=report.issues
            or [OverviewIssue(title="No issues reported", body="The arm returned no issues.")],
            recommendation=report.recommendation,
        ),
        detailed_comments=report.detailed_comments,
    )


def run_pipeline(paper_dir: Path, model: str, *, refute: bool = False) -> Review:
    """The current pipeline, fed the same extracted markdown as every other arm."""
    from coarse.pipeline import review_paper

    review, _markdown, _paper_text = review_paper(
        paper_dir / "paper.md",
        model=model,
        skip_cost_gate=True,
        refute=refute,
    )
    return review


def run_agent(
    markdown: str,
    structure: PaperStructure,
    client: LLMClient,
    *,
    mode: str,
    workspace_root: Path,
    max_targets: int,
    max_parallel: int,
    rounds: int = 1,
) -> tuple[Review, list, object]:
    from coarse.agent.orchestrator import run_agentic_review

    return run_agentic_review(
        markdown,
        structure,
        client,
        mode=mode,  # type: ignore[arg-type]
        max_targets=max_targets,
        max_parallel=max_parallel,
        workspace_root=str(workspace_root),
        keep_workspace=True,
        rounds=rounds,
        # Without this a rounds=2 run emits no arm A, and the save side below
        # is guarded by ``is_file()``, so the pairing is skipped in silence.
        # That is what happened to the first four paired runs; see
        # evals/PREREGISTRATION_xref.md.
        emit_round1_review=rounds > 1,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", required=True, type=Path)
    ap.add_argument(
        "--arm",
        required=True,
        choices=[
            "baseline",
            "pipeline",
            "pipeline_refuted",
            "agent_single",
            "agent_swarm",
            "agent_swarm_r1",
            "agent_swarm_xref",
            "agent_sweep",
        ],
    )
    ap.add_argument("--model", default="openrouter/anthropic/claude-opus-5.5")
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--max-targets", type=int, default=10)
    ap.add_argument("--max-parallel", type=int, default=4)
    ap.add_argument("--out", type=Path, default=Path("evals/runs"))
    args = ap.parse_args()

    markdown, structure = _load(args.paper)
    paper_id = args.paper.name
    tag = f"{paper_id}__{args.arm}__run{args.run}"
    out_dir = args.out / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    client = LLMClient(model=args.model, config=load_config())
    started = time.monotonic()
    records: list = []

    if args.arm == "baseline":
        review = run_baseline(markdown, structure, client)
    elif args.arm in {"pipeline", "pipeline_refuted"}:
        review = run_pipeline(args.paper, args.model, refute=args.arm == "pipeline_refuted")
    else:
        mode = {"agent_single": "single", "agent_sweep": "sweep"}.get(args.arm, "swarm")
        rounds = 2 if args.arm == "agent_swarm_xref" else 1
        review, records, workspace = run_agent(
            markdown,
            structure,
            client,
            mode=mode,
            workspace_root=out_dir / "workspace",
            max_targets=args.max_targets,
            max_parallel=args.max_parallel,
            rounds=rounds,
        )
        logger.info("workspace kept at %s", workspace.root)

    elapsed = time.monotonic() - started
    verified, before, after = _finalize(review, markdown)

    (out_dir / "review.json").write_text(verified.model_dump_json(indent=1), encoding="utf-8")
    (out_dir / "review.md").write_text(render_review(verified), encoding="utf-8")
    meta = {
        "paper": paper_id,
        "arm": args.arm,
        "run": args.run,
        "model": args.model,
        "elapsed_s": round(elapsed, 1),
        "cost_usd": round(client.cost_usd, 4),
        "comments_before_quote_verify": before,
        "comments_after_quote_verify": after,
        "quote_drop_rate": round(1 - after / before, 3) if before else None,
        "n_overall_issues": len(verified.overall_feedback.issues),
        "agents": [r.model_dump() for r in records],
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    # A rounds=2 run also emits the round-1-only review. Save it as its own run
    # so the two arms are scored identically; they share a plan, a first pass
    # and a set of round-1 verdicts, so the pair is matched on everything but
    # the second round. See evals/PREREGISTRATION_xref.md.
    round1_path = out_dir / "workspace" / "review_round1.json"
    if round1_path.is_file():
        paired_dir = args.out / f"{paper_id}__agent_swarm_r1__run{args.run}"
        paired_dir.mkdir(parents=True, exist_ok=True)
        round1 = Review.model_validate_json(round1_path.read_text(encoding="utf-8"))
        r1_verified, r1_before, r1_after = _finalize(round1, markdown)
        (paired_dir / "review.json").write_text(
            r1_verified.model_dump_json(indent=1), encoding="utf-8"
        )
        (paired_dir / "review.md").write_text(render_review(r1_verified), encoding="utf-8")
        (paired_dir / "meta.json").write_text(
            json.dumps(
                {
                    **meta,
                    "arm": "agent_swarm_r1",
                    "comments_before_quote_verify": r1_before,
                    "comments_after_quote_verify": r1_after,
                    "quote_drop_rate": round(1 - r1_after / r1_before, 3) if r1_before else None,
                    "n_overall_issues": len(r1_verified.overall_feedback.issues),
                    "paired_with": tag,
                },
                indent=1,
            ),
            encoding="utf-8",
        )
        print(f"paired round-1 arm saved to {paired_dir}")

    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
