# Preregistration: does the cross-reference round improve a swarm review?

Written and committed **before** the runs it analyses. Commit this file, then
run. The point is that three measurements in this branch have already been
withdrawn after the fact, twice because the analysis was chosen once the
numbers were visible.

## Question

In `coarse.agent.orchestrator`, `rounds=2` adds a cross-reference round: after
the first investigation pass, a digest of every candidate finding is written to
the workspace and each investigator is re-run with it, asking what those leads
imply for its own part of the paper. Does that round improve the review?

Evidence so far on `psi`, which prompted this: baseline swarm over five runs
reached 3, 5, 5, 5 and 7 of 16 reference findings at 100% precision every time;
two cross-reference runs reached 5 and 8 of 16 at 87% and 100%. The 8 is the
highest recall any swarm run has reached and the 87% is the only precision
failure in seven runs. Two observations against five cannot separate either
from variance.

## Design

**Paired, not two-sample.** The dominant noise source is the planner: it emits
different investigation targets on every run, and recall follows the targets.
Comparing independent runs spends most of its power on that variance. Because
the cross-reference round is an *increment* on the first pass, one run can emit
both reviews:

1. run the planner and the first investigation pass;
2. refute those findings, run the editor over the survivors, emit **arm A**
   (round-1 only — identical to what `rounds=1` would have produced from this
   plan);
3. run the cross-reference round, refute its findings, run the editor over all
   survivors, emit **arm B** (rounds 1 and 2).

Both arms therefore share one plan, one first pass and one set of round-1
verdicts. The only difference between them is the increment the second round
contributed. Each run is one matched pair.

**Runs:** 4 paired runs on `psi`, `--max-targets 8`, model
`anthropic/claude-opus-5.5`, one extraction shared by every run.

`coset_codes` is excluded deliberately: its swarm recall is 1/25 and 2/25
across runs, structurally capped by a reference whose items are mostly phrased
as reading difficulties that an agent held to demonstrate a defect will never
report. It cannot move either way, so including it would only add cost.

## Metrics, per arm, per run

- **Recall:** reference findings matched, of 16 (`evals/references/psi.json`).
- **Precision:** share of adjudicated claims the judge calls supported.
- **Substantive precision:** share it calls supported *and* substantive. This
  is the headline precision figure; supported alone is satisfiable by hedging.
- **Bad claims:** adjudicated claims that are not supported-and-substantive.
- Cost and wall-clock.

Scoring is unchanged from the rest of this document: top-20 normalization, both
detailed comments and macro issues adjudicated, judge
`openai/gpt-5.6-terra-pro`, a different family from the arms under test.

## Decision rule

Let `d_recall` be B minus A within a run, and likewise `d_bad`.

**Ship the round on** (make `rounds=2` the swarm default) only if **both**:

1. mean `d_recall` >= +1.0 finding, and at least 3 of 4 runs have
   `d_recall` >= 0; and
2. mean `d_bad` <= 0, and no run has `d_bad` >= +2.

**Delete the round** if mean `d_recall` <= 0, or if two or more runs have
`d_bad` >= +2.

**Otherwise leave it as it is now**: implemented, `rounds=1` default, documented
as unresolved. This is the honest outcome if the increment is small relative to
the spread, and it is the outcome I expect on four pairs.

## Committed in advance

- Four pairs is thin. With a baseline spread of 3 to 7 findings, this design can
  detect roughly a one-finding mean shift and not much less. If the result lands
  inside the "otherwise" branch, that is the finding, and it will not be
  reported as a win for either side.
- No run will be dropped after the fact. A run that errors is reported as an
  error and replaced, and both facts are stated.
- The per-run numbers go in the write-up, not only the means.
- If arm B's extra claims are judged supported but **not** substantive, that is
  reported as a hedging gain and counts against the round, not for it. The
  `substantive` flag exists because an is-this-supported test alone has already
  misled this branch once.

## Deviation, recorded 2026-11-23, before any scoring

The four runs executed and exited 0, but **no arm A was emitted**. `run_arm.py`
set `rounds=2` and then looked for `workspace/review_round1.json`, while
`run_agentic_review` writes that file only when `emit_round1_review=True`,
which the harness never passed. The save side was guarded by
`if round1_path.is_file()`, so the pairing was skipped in silence. The
orchestrator tests covered the flag and passed; nothing asserted that the eval
harness sets it. The flag is now wired and a test asserts the harness produces
the file.

**Recovery: arm A is reconstructed, the runs are not repeated.** Everything
arm A needs was written to the kept workspace before the second round began:

- `findings/<id>.json` for every candidate, where a cross-reference finding
  carries an `x` in its target id (`t06x-f1`), so the two rounds separate
  exactly;
- `findings/<id>.verdict.json` for every candidate, holding the full verdict
  including the two fields the editor prompt actually reads,
  `corrected_claim` and `severity_after_review`. Only the verdict *label* is
  in `run.json`; the objects are on disk, which is what makes this possible.

So arm A is produced by running the same `_assemble` over the round-1
confirmed findings and their stored verdicts, in a fresh workspace built from
the same `paper.md` and containing only those findings and no board. That is
the same stage over frozen inputs: the planner, the first pass and the
round-1 verdicts were all fixed before any of this was known, and no refuter
is re-rolled. `notes/` is empty in all four runs, so arm A is not handicapped
by starting from an empty notes directory.

The reconstruction is marked `"reconstructed": true` in each arm-A
`meta.json`.

**What this costs in credibility.** Arm A's editor call happens in a later
process than arm B's, and after the round-2 counts were visible. The counts
were visible; no score was. The thresholds in the decision rule above are
unchanged, both arms are scored in a single pass, and this note is committed
before that pass runs.

**Also now known, and reported rather than acted on:** the agent editor
applies `corrected_claim` when a refuter supplies one
(`_render_findings_for_editor`), while the pipeline gate in
`agent/refutation.py` deliberately does not, because applying it was measured
to be the source of that stage's apparent precision gain. That inconsistency
is real and predates these runs. Changing it now would alter both arms
mid-experiment, so it stays as it is and is written up as an open item.

## Outcome, 2026-11-23

Four matched pairs on `psi`. Arm B minus arm A:

| run | round-2 findings | recall A | recall B | d_recall | good A | good B | d_good | bad A | bad B | d_bad |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 9/16 | 9/16 | 0 | 16 | 17 | +1 | 0 | 0 | 0 |
| 21 | 1 | 8/16 | 9/16 | +1 | 14 | 15 | +1 | 3 | 2 | −1 |
| 22 | 0 | 3/16 | 4/16 | +1 | 6 | 6 | 0 | 2 | 2 | 0 |
| 23 | 4 | 7/16 | 7/16 | 0 | 11 | 13 | +2 | 2 | 4 | +2 |

Mean `d_recall` +0.50, below the +1.0 ship threshold. Mean `d_bad` +0.25, above
the ship threshold of 0. Mean `d_recall` is above 0 and only one run has
`d_bad` >= +2, so the delete branch does not fire.

**Verdict: leave it as it is.** `rounds=2` implemented, `rounds=1` default, off.
This is the branch the design section said it expected on four pairs, and per
the commitment above it is **not reported as a win for either side**.
Thresholds were not touched; `evals/analyze_xref.py` applies them and writes
`evals/runs/xref_analysis.json`.

What the table does not show, and what keeps this unresolved:

- **Run 22 is the noise floor.** Its second round produced no findings, so both
  arms handed the editor identical inputs and produced identical comment and
  claim counts. Recall still differed by one. A single pair therefore carries
  ±1 reference finding of editor-plus-judge noise. That is the size of the
  round's apparent gain, and it equally means four pairs cannot establish that
  the round does nothing.
- **Recall cannot see most of the round's output.** Six confirmed findings
  across the four pairs, four of which became supported-and-substantive claims,
  and only one of those four was a reference item. The reference is a fixed list
  of 16, so a demonstrated defect absent from it scores zero by construction.
  `d_good` is where the round shows up, and it is non-negative in all four pairs
  and positive in three.
- **One gain is traceable end to end.** Run 21's round-2 finding is that
  Proposition 3's step count depends on the variance estimate, so the stability
  level Proposition 2 matches is data-dependent. It becomes arm B's comment 11
  and matches reference finding O1b; arm A has no comment on that defect.
- **Run 23's `d_bad` of +2 is not cleanly the round's.** Decomposed: the editor
  dropped one round-1 bad claim arm A published, created another by splitting
  the round-1 variance-estimate material into a comment that then failed
  adjudication, and the round itself added two — one genuine miss the refuter
  passed, and one where the round found a real constant mismatch
  (`(1/δ)kη²` against Proposition 2(a)'s `½kη²`) that the editor then wrote up
  as "a typo in the final ε", which the judge called cosmetic. Round-1 claims
  flip between arms in run 21 too. The `bad` column is as noisy as the recall
  column, for the same reason: each arm runs its own editor.

Two measurement limitations to record. The judge's `substantive` field defaults
to `True` when the judge omits it, so the good count is an upper bound and
`d_bad` is, if anything, understated; the field was present and varying on
every claim checked. And the recall metric credits only reference items, which
is the binding constraint on this experiment rather than the thresholds — fixing
it means rescoring every arm in `docs/AGENTIC_REVIEW.md`, not just these pairs.
