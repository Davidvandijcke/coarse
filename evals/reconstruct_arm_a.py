"""Rebuild the paired round-1 arm from a kept rounds=2 workspace.

Needed because the first four paired runs emitted no arm A: ``run_arm.py`` set
``rounds=2`` without ``emit_round1_review``, and the save side was guarded by
``is_file()``, so the pairing was skipped in silence. See
evals/PREREGISTRATION_xref.md for the recorded deviation.

Everything arm A needs was written to the workspace before the second round
began. A cross-reference finding carries an ``x`` in its target id, so the two
rounds separate exactly, and each candidate has its full verdict on disk
including the two fields the editor prompt reads. This therefore runs the same
``_assemble`` over frozen inputs in a fresh workspace holding only the round-1
findings and no board. Nothing is re-rolled: no planner, no investigator, no
refuter. The one new call per run is the editor.

Usage:
    OPENROUTER_API_KEY=... uv run python evals/reconstruct_arm_a.py \
        --runs evals/runs/psi__agent_swarm_xref__run20 ...
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import sys
from pathlib import Path

from coarse.agent.orchestrator import _assemble
from coarse.agent.types import LedgerFinding, RefutationVerdict
from coarse.agent.workspace import ReviewWorkspace
from coarse.config import load_config
from coarse.llm import LLMClient
from coarse.synthesis import render_review
from coarse.types import PaperStructure

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("reconstruct")


def _run_arm_module():
    """Reuse the harness's own ``_finalize`` so both arms are finished alike."""
    path = Path(__file__).with_name("run_arm.py")
    spec = importlib.util.spec_from_file_location("_eval_run_arm", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["_eval_run_arm"] = module
    spec.loader.exec_module(module)
    return module


def _round1(run_dir: Path) -> tuple[list[LedgerFinding], dict[str, RefutationVerdict]]:
    """Load the confirmed round-1 findings and their stored verdicts.

    A cross-reference finding's ``target_id`` ends in ``x``, which is how the
    second round's output is excluded. The verdicts are read from disk rather
    than re-derived, so arm A and arm B share one set of round-1 verdicts
    exactly as the paired design requires.
    """
    findings_dir = run_dir / "workspace" / "findings"
    findings: list[LedgerFinding] = []
    verdicts: dict[str, RefutationVerdict] = {}
    for path in sorted(findings_dir.glob("*.json")):
        if path.name.endswith(".verdict.json"):
            continue
        finding = LedgerFinding.model_validate_json(path.read_text(encoding="utf-8"))
        if finding.target_id.endswith("x"):
            continue
        verdict_path = path.with_suffix(".verdict.json")
        if verdict_path.is_file():
            verdict = RefutationVerdict.model_validate_json(
                verdict_path.read_text(encoding="utf-8")
            )
            if verdict.verdict != "confirmed":
                continue
            verdicts[finding.finding_id] = verdict
        findings.append(finding)
    return findings, verdicts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, type=Path)
    ap.add_argument("--paper", required=True, type=Path)
    ap.add_argument("--model", default="openrouter/anthropic/claude-opus-5.5")
    ap.add_argument("--out", type=Path, default=Path("evals/runs"))
    args = ap.parse_args()

    run_arm = _run_arm_module()
    structure = PaperStructure.model_validate_json(
        (args.paper / "structure.json").read_text(encoding="utf-8")
    )

    for run_dir in args.runs:
        source_meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
        # The run's own extracted markdown, not the paper dir's, so arm A is
        # built on exactly the text arm B saw.
        markdown = (run_dir / "workspace" / "paper.md").read_text(encoding="utf-8")
        findings, verdicts = _round1(run_dir)
        logger.info("%s: %d confirmed round-1 finding(s)", run_dir.name, len(findings))

        client = LLMClient(model=args.model, config=load_config())
        records: list = []
        workspace = ReviewWorkspace.create(markdown, structure)
        try:
            for finding in findings:
                workspace.write_finding(finding)
            review, unlinked = _assemble(
                client,
                workspace,
                structure,
                findings,
                verdicts,
                author_notes=None,
                language=None,
                records=records,
            )
        finally:
            workspace.cleanup()

        # ``_assemble`` falls back to a deterministic ledger render when the
        # editor fails, which is right in production and wrong here: it would
        # hand arm A a plainer report than arm B got and the pair would no
        # longer be matched on the editor. A first attempt at this
        # reconstruction 401'd on every call and produced exactly that, so
        # refuse to write anything unless the editor really ran.
        editor = [r for r in records if r.role == "editor"]
        if not editor or editor[0].error or client.cost_usd <= 0:
            raise SystemExit(
                f"{run_dir.name}: the editor did not run "
                f"(error={editor[0].error if editor else 'no record'!r}, "
                f"cost=${client.cost_usd:.4f}). Refusing to write a fallback "
                "report as arm A."
            )

        verified, before, after = run_arm._finalize(review, markdown)
        out_dir = args.out / f"{args.paper.name}__agent_swarm_r1__run{source_meta['run']}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "review.json").write_text(verified.model_dump_json(indent=1), encoding="utf-8")
        (out_dir / "review.md").write_text(render_review(verified), encoding="utf-8")
        (out_dir / "meta.json").write_text(
            json.dumps(
                {
                    **source_meta,
                    "arm": "agent_swarm_r1",
                    "reconstructed": True,
                    "paired_with": run_dir.name,
                    "round1_confirmed_findings": len(findings),
                    "cost_usd": round(client.cost_usd, 4),
                    "comments_before_quote_verify": before,
                    "comments_after_quote_verify": after,
                    "quote_drop_rate": round(1 - after / before, 3) if before else None,
                    "n_overall_issues": len(verified.overall_feedback.issues),
                    "comments_dropped_unlinked": len(unlinked),
                    "agents": [r.model_dump() for r in records],
                },
                indent=1,
            ),
            encoding="utf-8",
        )
        print(
            f"{out_dir.name}: {len(findings)} round-1 findings -> "
            f"{after} comment(s), {len(verified.overall_feedback.issues)} issue(s), "
            f"${client.cost_usd:.4f}"
        )


if __name__ == "__main__":
    main()
