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
