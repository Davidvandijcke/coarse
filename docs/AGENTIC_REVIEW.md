# Agentic review: diagnosis, design and measurement

Status: in progress on `feat/agentic-review-harness`.
Relates to #264 (bounded tools, paper context broker, evidence ledger), #270
(same-model ablation), #279 (host isolation), #260 (abstention).

## What this work is for

Reviews of theory-heavy papers miss the findings a careful referee produces,
and some of what the pipeline does produce is confidently wrong (see the
Slutsky case: a review that scored 6/6 on the quality judge and was rejected
outright by the paper's author). This document records a measured diagnosis of
where findings are lost and where false ones come from, the smallest harness
change that addresses what the diagnosis found, and the measurement that
decides which parts are worth shipping.

Two papers are used. `psi` (*Post-Selection Inference via Algorithmic
Stability*, arXiv 2011.09462v2) is the paper the diagnosis was done on; a
current-generation reference review of it is available, truncated to five macro
issues and six detailed comments, which atomize to 16 findings in
`evals/references/psi.json`. `coset_codes` is held out, with its own reference
review, atomized mechanically by `evals/prepare_paper.py` to 25 findings.

## Diagnosis

### Every appendix was discarded before review

`review_paper` filtered sections and then truncated to
`MAX_REVIEWABLE_SECTIONS = 25`. On `psi`, `structure.analyze_structure` returns
41 sections and the filter removed none, so the truncation decided the review's
scope. The last section reviewed was "9.2 Bernoulli design". The 16 after it
were never seen by any agent, including:

```
A.7  Proof of Proposition 1                         5,805 chars
A.9  Generalization and proof of Claim 5            3,487
A.10 Proof of Proposition 2 (LASSO stability)      14,263
A.12 Proof of Proposition 4                         5,252
B    Deferred numerical results                     5,571
C    Generalizations of stable algorithms           6,176
```

All six of the reference review's detailed comments are in A.10, A.11 and
Lemma 5. Three of its five macro issues depend on Appendix B, Appendix C or
A.9. Of the 16 atomized findings, 13 require a section the pipeline discarded.
No prompt revision or model upgrade recovers those, because the text never
reaches a prompt.

Two structure defects compound it:

- **A section whose heading the parser mangled was filtered by title.** When a
  page break falls immediately before a heading, the parser titles the section
  `<!-- PAGE BREAK -->` and leaves the real heading in the body. On `psi` one
  such section is 1,107 characters of "A.6 Proof of Theorem 2", the proof of
  the paper's central result, and the reference review's critical finding is
  about a step in it. An earlier version of the fix in this branch dropped it.
- **A.11 is not parsed as a section at all**; its text is absorbed into A.10.
  A.6 and A.8 are likewise missing. Two reference findings (D4, D6) are in
  A.11. The mis-parsing in `structure.py` is untouched here.

### The capabilities the reference findings require

| Capability | Findings (of 16) |
|---|---|
| Read a section the pipeline discarded | 13 |
| Compare two separated locations in the paper | 12 |
| Carry out algebra or a numeric instantiation | 9 |
| Construct an edge case | 1 |

Cross-location comparison is the second gap. A section agent receives
`truncate_section(section)`, the abstract, precomputed claims and definitions,
and a notation block; it cannot retrieve any other part of the paper. The
reference findings are mostly of the form "the proof in A.10 does not establish
what Definition 2 requires", "the premise of Lemma 3(b) is one-sided", "the
displayed gradient disagrees with Algorithm 5", "Appendix B's delta exceeds
Section 9's alpha". Each needs two locations side by side.

Computation is the third. "The first upper bound is half the exact curvature",
"for n = 50 and k = 20 roughly six rows remain", "the expression is negative
despite bounding a nonnegative quantity" are all checkable by differentiating,
substituting or evaluating. A text-only model does this in its head, which is
where the Slutsky failure happened.

## Design

A bounded tool runtime rather than wider prompts.

### Workspace

One ephemeral directory per review, outside the repository and the user's
project:

```
paper.md              full extracted markdown
sections/NNN-slug.md  one file per parsed section
outline.md            section index with character offsets
findings/<id>.json    evidence ledger, one file per candidate finding
notes/<agent>.md      per-agent scratch space
```

The workspace is the medium the agents collaborate through: an investigator
writes a candidate finding as a ledger file and a refuter reads that file and
writes its verdict beside it. No review content passes between agents as
conversational state.

### Tools

Implemented in-tree, not inherited from a host CLI, so the same runtime works
on the hosted BYOK path where no coding-agent CLI exists:

- `paper_search(query, regex)` - search the whole paper, returning matches with
  section and character anchors.
- `paper_read(section_id | char_start, length)` - exact passage retrieval.
- `paper_outline()` - every section with length and whether it holds mathematics.
- `python(code)` - bounded subprocess with `sympy` and `numpy`.
- `note_write` / `note_list` / `note_read` - shared scratch space inside the
  workspace.

There is no web search and no citation checking. The literature stage is
unchanged and still runs only on the staged path.

`python` is bounded by a wall-clock timeout, an address-space cap, `-I`
isolated mode, and a scratch cwd. Network denial is enforced by the OS where a
mechanism exists (a deny-network seatbelt profile under `sandbox-exec` on
macOS, `unshare --net` on Linux where permitted) and is **not** enforced
otherwise; `sandbox.available_isolation()` reports which case applies and the
tool description shown to the model is generated from it. The filesystem is not
confined in any mode. It runs code the model wrote, never code taken from the
paper.

### Roles

1. **Planner** - reads the outline, abstract, introduction and the paper's
   labelled objects, and emits claim-shaped investigation targets rather than
   section-shaped ones. If it submits nothing, targets are derived
   deterministically from the paper's structure.
2. **Investigators**, in parallel, one per target, each with whole-paper
   retrieval and computation. Zero findings is a valid result (#260).
3. **Refuters**, one per candidate finding, in a fresh context holding the
   claim, its location and the paper passages it points at, but **not** the
   investigator's reasoning or its computation transcript: a refuter shown the
   derivation audits the derivation rather than the paper. A finding it does
   not reproduce is dropped. This is the mechanism the agent-swarm literature
   reports as the defence against a swarm amplifying its own error - every
   result verified by a fresh agent with no shared memory of the work
   ([Gusev and Bernal Neira 2026](https://arxiv.org/abs/2609.35719), section 4.1).
4. **Editor** - writes from surviving ledger entries only. Each comment carries
   the finding id it reports, and a comment whose id is not in the confirmed set
   is dropped in code rather than merely discouraged by the prompt.

There is one refutation pass, not a negotiation: agents do not exchange
messages back and forth.

`quote_verify` and `synthesis` stay deterministic and shared with the staged
path, so the verbatim-quote guarantee is identical.

### Modes and entry points

- `coarse review --refute` - keep the staged pipeline as the generator and send
  every comment that survives the editorial filter, and every macro issue, to a
  refuter. A comment is kept or dropped; an issue is narrowed by deleting the
  spans the refuter names.
- `coarse review --agent sweep|swarm|single` - review through the agent runtime
  instead. `swarm` uses planner-divided targets; `sweep` divides every
  reviewable section into contiguous regions and briefs each investigator for
  breadth; `single` is one whole-paper referee.
- `review_paper(refute=..., agent_mode=...)` for library callers.

All are off by default.

### Host isolation

`ClaudeCodeClient` runs `claude -p` with no isolation: ambient MCP servers,
hooks, settings, skills and the caller's working directory are all inherited
(#279). A paper is untrusted input, so any tool-enabled run through a host CLI
needs isolating first. The flags that do it while preserving subscription
authentication are `--strict-mcp-config` with no `--mcp-config`,
`--setting-sources ""`, `--disable-slash-commands`, `--no-session-persistence`,
an explicit `--tools`/`--allowedTools` allowlist, and a working directory set to
the workspace. `--bare` is not usable: it forces `ANTHROPIC_API_KEY` and so
defeats the subscription path. Host-CLI backends are kept behind the same runner
interface but are not the primary path, and this isolation work is not done in
this branch.

## Measured results

One model (`anthropic/claude-opus-5.5` via OpenRouter), one extraction per
paper shared by every arm, top-20 comment normalization. Recall is scored
against the atomized reference findings. Precision adjudicates every claim a
review makes - detailed comments and macro issues alike - against the paper
itself, by a judge from a different model family
(`openai/gpt-5.6-terra-pro`) so no model grades its own prose.

### psi (16 reference findings)

| arm | comments | issues | recall | precision | of comments | unsupported | cost | time |
|---|---|---|---|---|---|---|---|---|
| pipeline, before the section fix | 21 | 11 | 56% | 52% | 60% | 15 of 32 | n/a | 442s |
| pipeline, after the section fix | 25 | 11 | **69%** | 68% | 70% | 10 of 36 | n/a | 504s |
| baseline, one full-paper prompt | 14 | 5 | 56% | 95% | 93% | 1 of 19 | $0.65 | 166s |
| single agent with tools | 6 | 4 | 25% | 100% | 100% | 0 of 10 | $1.05 | 492s |
| swarm, structural targets | 7 | 4 | 19% | 100% | 100% | 0 of 11 | $2.09 | 547s |
| swarm, structural targets | 6 | 5 | 31% | 100% | 100% | 0 of 11 | $3.38 | 772s |
| swarm, planner working | 9 | 4 | 44% | 100% | 100% | 0 of 13 | $2.98 | 814s |
| sweep | 7 | 4 | 25% | 100% | 100% | 0 of 11 | $5.09 | 949s |

### coset_codes, held out (25 reference findings)

| arm | comments | issues | recall | precision | of comments | unsupported | cost | time |
|---|---|---|---|---|---|---|---|---|
| pipeline | 19 | 12 | **40%** | 48% | 58% | 16 of 31 | n/a | 546s |
| baseline, one full-paper prompt | 20 | 6 | 20% | 96% | 100% | 1 of 26 | $1.06 | 290s |
| swarm, structural targets | 3 | 3 | 8% | 83% | 100% | 1 of 6 | $2.06 | 731s |
| sweep | 12 | 5 | 12% | 94% | 92% | 1 of 17 | $3.93 | 738s |

### What refutation is worth

Measured on identical generation: the refuter runs over a review the judge has
already adjudicated, every claim it leaves untouched keeps its stored verdict,
and only text it changed is re-judged. Counts rather than rates, because a rate
hides the trade. "Good" means the judge called the claim both supported by the
paper and substantive; the stricter test matters because an
is-this-supported test alone is satisfiable by hedging.

| paper | before | after | trade |
|---|---|---|---|
| `psi` (run A) | 20 good, 11 bad | 19 good, 7 bad | −4 bad, −1 good |
| `psi` (run B) | 20 good, 11 bad | 19 good, 7 bad | −4 bad, −1 good |
| `coset_codes` | 14 good, 17 bad | 14 good, 10 bad | −7 bad, 0 good |
| `targeting` | 26 good, 6 bad | 26 good, 6 bad | no change |

Net, the gate removed 11 bad claims and cost 1 good one, at about $1.85 and 31
to 36 agent calls per paper. Gross, which is the number to judge it on:

| | count |
|---|---|
| bad comments dropped | 9 |
| good claims dropped | 3 (one `psi` issue, two `coset_codes` comments) |
| bad issues that became good when their narrowed text was re-judged | 2 |

The net figure nets those two flips against the three losses. Both flips are on
`coset_codes`, and they came from a judge that has been seen to change verdict
on byte-identical text, so the macro-issue half's entire upside rests on two
re-judgements of exactly the kind this measurement otherwise takes pains to
exclude.

**Coverage survives the gate.** Crossing each reference finding's matching
claim against what the gate did to that claim:

| paper | reference hits | carried by a kept claim | by a narrowed claim | by a dropped claim |
|---|---|---|---|---|
| `psi` | 11 | 8 | 3 | **0** |
| `coset_codes` | 10 | 5 | 5 | **0** |
| `targeting` | 4 | 4 | 0 | **0** |

No reference finding was carried by a claim the gate dropped. Eight ride on a
narrowed claim, where a deletion could in principle have removed the part that
matched; re-scoring recall on the post-refutation reviews would settle that and
has not been done.

Three things in that table matter more than the totals.

**Only the comment half ships.** Split by half, over all three papers:

| half | bad removed | good lost |
|---|---|---|
| comments | 9 | 2 |
| macro issues | 2 | 1 (net +1 good) |

On `psi` the issue half was net *negative*: it converted no bad issue and
dropped a good one. On `coset_codes` it converted two, and both conversions are
re-judgements by a judge known to change verdict on identical text.

Reading the narrowed issues settled it. One `coset_codes` issue titled
"Multiplicity formulas rest on unverified uniformity assumptions" came back
with a body saying "That holds for the partitions checked here: 8 per coset for
$D_4/RD_4$ ... which reproduces the table's 44, 252, 764 and 316" — the
deletion had removed the criticism and left text confirming the assumption,
under a title still asserting the defect. A gate that can leave a heading
contradicting its own paragraph should not run on an author-facing review.

**So the macro-issue half was removed.** `refute_issues`, `narrow_by_deletion`
and `IssueVerdict` are in this branch's history if it is ever worth revisiting
with more papers and a verdict-stable judge; nothing in the shipped path
touches the overall feedback. `--refute` is comments only.

**On a review that was already good, the gate is nearly inert.** `targeting` is
the only paper no design decision here has touched. Its pipeline review was
already 26 good to 6 bad, the gate dropped nothing, and its three narrowings
changed no verdict. That is the right failure mode — a gate that cannot find
anything should not damage the review — but it also means the gate adds nothing
where the generator was already accurate, so its value depends on the paper.

**Two `psi` runs gave the same counts.** They are genuinely separate runs
($1.72 and $1.76) and both report 22 claims unchanged, 4 narrowed, 5 dropped
with identical verdict counts. That is two observations compared on counts
alone, and the second overwrote the first's per-claim record, so it is not
evidence that the gate is deterministic — and it cannot be credited to making
the gate subtractive, since the comment refuter's prompt and drop rule did not
change. Earlier runs of the rewriting version dropped 4, then 5, then 6 of the
same comments, so the variance seen then may simply not have recurred.

### Three retracted measurements, and what they changed

Each of these would have shipped a false claim, and the third changed the
design rather than the measurement. They are recorded because the mistakes are
easy to repeat.

1. **Comparing a `pipeline_refuted` run with a `pipeline` run.** Two different
   reviews, so nothing was attributable to the gate.
2. **Scoring a post-refutation review end to end.** That re-judges claims the
   gate left untouched, and the judge drifts: the arithmetic did not close
   (the gate's own actions capped one paper at 7 of 10 supported issues while
   the score reported 8), and a byte-identical review scored 13 of 20 and then
   12 of 20 on two passes. Fixed by carrying stored verdicts forward.
3. **Scoring "is this claim supported by the paper?" alone.** The gate was
   rewriting comments as well as dropping them, and sampling the rewrites found
   ones that retreated from "X is wrong" to "the paper does not say how X was
   handled". That satisfies the supported test while giving the author less, so
   the metric was rewarding a hedge: the same run gained 13 points on
   "supported" and 6 on "supported and substantive".

Reading the saved reviews rather than the verdicts found two more defects no
verdict would have shown: every narrowed issue body came back *longer* than the
one it replaced (1.0x to 1.6x), each prefixed with the issue title, against the
prompt's explicit instruction to say less and never more.

So the gate became purely subtractive. A comment is kept or dropped and never
rewritten, and the refuter's suggested wording stays on the verdict for a human
to weigh. An issue is narrowed only by deleting verbatim spans the refuter
names, so every surviving word is the reviewer's own; a span that does not
occur in the body removes nothing, and naming every span drops the issue.

### The cross-reference round: measured, still unresolved, off by default

The swarm's deficiency is coverage, and its investigators work in isolation, so
the obvious thing to try is letting them see each other's findings. `rounds=2`
writes a digest of every candidate finding to the workspace and re-runs each
investigator with it, asking what those leads imply for its own part of the
paper. The digest carries no reasoning or computation, the brief forbids
repeating or relying on an entry, and everything the round produces still
passes the independent refuter.

Decision rule, fixed before any number was seen: **recall must rise outside the
baseline range and precision must not fall.**

`psi`, same code, same extraction:

| arm | run | comments | recall | precision | unsupported | cost |
|---|---|---|---|---|---|---|
| swarm | 1 | 7 | 3/16 | 100% | 0 | $2.09 |
| swarm | 2 | 6 | 5/16 | 100% | 0 | $3.38 |
| swarm | 3 | 9 | 7/16 | 100% | 0 | $2.98 |
| swarm | 10 | 4 | 5/16 | 100% | 0 | $2.47 |
| swarm | 11 | 6 | 5/16 | 100% | 0 | $1.93 |
| **swarm + xref** | 10 | 11 | 5/16 | **87%** | **2** | $3.75 |
| **swarm + xref** | 11 | 10 | **8/16** | 100% | 0 | $3.55 |

Baseline: five runs, 3 to 7 of 16, mean 5.0, precision 100% every time.
Cross-reference: two runs, 5 and 8 of 16, mean 6.5.

**The rule is not met, so it is not shipped on.** `rounds=1` remains the
default and the existing path is untouched. Precision fell in one of the two
cross-reference runs, against 100% in five of five baseline runs, and that is
the disqualifying condition.

**At this point the result was ambiguous rather than negative.** The 8 of 16 in
run 11 is the highest recall any swarm run had reached, above the baseline
ceiling of 7, at unchanged precision. Two observations against five, with a
baseline spread of 3 to 7, cannot separate that from variance: one run two
standard deviations above a five-run mean is suggestive and nothing more. The
paired runs below were built to settle it. They remove the planner variance
and return a verdict of keep-it-off, but they do not settle it.

The mechanism does fire. Three of ten candidates came from the second round in
each run, and across the two runs they include the curvature constant
understated by a factor of two and Lemma 5 stated for arbitrary step sizes
(reference findings D6 and D5).

What the failing run shows is the cost. The round-1 finding "with estimated
sigma-hat the LASSO oracle still depends on the data" went onto the board and
came back written up twice, once as a comment and once as a macro issue, and
the adjudicator rejects both: the scores and the Laplace noise are scaled by
the same 1/sigma-hat, so the selection is invariant to it. **The refuter
confirmed all eight candidates in that run.** The gate built specifically as
the defence against a claim spreading without being demonstrated did not catch
it, which is worth recording separately from the round's own result — it bounds
how much that gate can be trusted to carry anywhere else in this design.

`coset_codes` cannot contribute either way: its swarm recall is 1/25 and 2/25
across runs, structurally capped by a reference whose items are mostly phrased
as reading difficulties that an agent held to demonstrate a defect will never
report.

#### A paired design: the rule says keep it off, and it is not settled

Four unpaired runs per arm would have spent most of their power on planner
variance, which is what produced the 3-to-7 spread above. The round is an
increment on the first pass, so one run can emit both arms instead: refute
round 1, run the editor over the survivors and emit **arm A**, then run the
cross-reference round, refute only its findings, and run the editor again over
everything to emit **arm B**. Both arms share one plan, one first pass and one
set of round-1 verdicts, so each run is a matched pair and the pairing costs
one extra editor call. The decision rule, the metrics and the thresholds were
written and committed before the runs in `evals/PREREGISTRATION_xref.md`, and
`evals/analyze_xref.py` holds the thresholds as module constants so moving one
shows up in a diff. "Good" counts claims the judge calls supported *and*
substantive; "bad" is every other adjudicated claim, because supported alone is
satisfiable by hedging.

| run | round-2 findings | recall A | recall B | d | good A | good B | d | bad A | bad B | d |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 9/16 | 9/16 | 0 | 16 | 17 | +1 | 0 | 0 | 0 |
| 21 | 1 | 8/16 | 9/16 | +1 | 14 | 15 | +1 | 3 | 2 | −1 |
| 22 | **0** | 3/16 | 4/16 | +1 | 6 | 6 | 0 | 2 | 2 | 0 |
| 23 | 4 | 7/16 | 7/16 | 0 | 11 | 13 | +2 | 2 | 4 | +2 |

Mean `d_recall` +0.50, below the +1.0 ship threshold; mean `d_bad` +0.25, above
the ship threshold of 0. Mean `d_recall` is above 0 and only one run has
`d_bad` >= +2, so the delete branch does not fire either. **The preregistered
verdict is "leave it as it is": implemented, `rounds=1` default, off.** That is
what ships. What follows is why the experiment did not settle the question the
rule was standing in for.

**Run 22 gives the noise floor, and it is the size of the effect.** Its
cross-reference round produced no findings at all, so both arms handed the
editor the identical four findings and both produced four comments and eight
adjudicated claims — and recall still differed by one. So a single pair carries
±1 reference finding of editor-plus-judge noise. That cuts both ways: it is the
same size as the round's apparent gain, and it also means four pairs cannot
establish that the round does nothing.

**Recall cannot see most of what the round produced.** Across the four pairs the
round contributed six confirmed findings, and four of them became supported-and-
substantive claims. Only one of those four was a reference item. The reference
is a fixed list of 16 findings, so a correct, demonstrated defect that is not on
it scores zero on the headline metric by construction. The `good` column is
where the round's output actually shows up, and it rose in three pairs of four.

Per-finding, in run 23, where the round contributed most:

| round-2 finding | became | adjudicated |
|---|---|---|
| experiments never say where the variance estimate comes from | "Variance input in the simulations is unspecified" | supported, substantive |
| A.3's "special case" does not cover Algorithm 3's procedure | "Claim 3 is not a special case of Proposition 4" | supported, substantive |
| A.10 concludes a `(1/δ)kη²` first term against Proposition 2(a)'s `½kη²` | "Typo in the final ε of A.10" | supported, **not substantive** |
| A.11's last step replaces the data-dependent σ̂ by σ | "Proposition 3's bound should involve σ̂" | **unsupported** |

So the round went 2 good, 2 bad in that run, and the two bad ones are worth
separating. The σ̂ claim is a genuine miss the refuter passed. The `(1/δ)kη²`
mismatch is a constant that does not match the proposition it is proving, and
the *editor* wrote it up as "a typo in the final ε", which the judge then
reasonably called cosmetic. The round found something real and the write-up
threw away its force.

**Run 23's net `d_bad` of +2 is not cleanly the round's, either.** Decomposed:
the editor dropped one round-1 bad claim that arm A published, created another
by splitting the round-1 σ̂ material into a second comment that then failed
adjudication, and the round itself added the two above. Round-1 claims flip
between arms in run 21 as well. The `bad` column is as noisy as the recall
column, and for the same reason: both arms run their own editor.

**What is actually known.** The mechanism fires and its output is mostly sound:
six findings, four good claims, one reference match traceable end to end — run
21's round-2 finding that Proposition 3's step count depends on the variance
estimate, so the stability level Proposition 2 matches is data-dependent, which
becomes arm B's comment 11 and matches reference finding O1b, with no
corresponding comment anywhere in arm A. What is not known is whether that is
worth roughly a third more cost per review, because the metric the rule was
written around cannot see four of the round's six findings and the per-pair
noise is the size of the effect. Settling it needs either more pairs or a
precision-weighted metric that credits a demonstrated defect which is not on
the reference list, and the second of those is a change to how every arm in
this document is scored.

The honest summary is the one the preregistration committed to in advance: this
landed in the "otherwise" branch, and it is not a win for either side.

### A second, stronger adjudication

The judge above answers from one prompt holding the whole paper, and it never
returned "unclear" on roughly 170 claims, which is not credible calibration.
It is also asked to do what the harness exists to do - look a definition up,
re-derive a step, check whether an objection is answered elsewhere - without
the means. `evals/adjudicate.py` re-runs the audit with a judge that has the
same workspace and tools the agents get.

It is **more lenient**, so the single-prompt precision figures above are too
harsh:

| run | single-prompt judge | tool-using judge |
|---|---|---|
| `coset_codes` pipeline (same 16 claims) | 48% | 69% |
| `psi` swarm, planner working (13 claims) | 100% | 92% |

The direction survives and the gap narrows. Of the six unsupported claims the
stronger judge found across both runs, five are objections the paper answers
elsewhere, and it names the location each time: "answered in Section 8.2",
"answered in Section II.E, immediately following the redundancy definition",
"answered in Section I-B". Even the agent arm's single failure is of that kind.

This is *consistent with* the diagnosis rather than independent confirmation of
it. The adjudicator's prompt names the hypothesis and it reports
`answered_elsewhere` as a field, so it was primed to look for exactly this. The
six items are in each run's `score_tool_judge.json` and are worth checking by
hand.

## What the numbers say

**The section truncation was real and fixing it helped.** Reviewing the
appendices took `psi` recall from 56% to 69% and precision from 52% to 68%.
This is the cheapest change here and it needs no agents.

**The staged pipeline's defect is precision, not coverage.** It leads on
coverage on both papers and also asserts the most claims the paper does not
support. The failure has one cause: the objection is answered in a part of the
paper a section agent cannot see.

**Independent refutation of the comments removes 9 bad claims for 2 good
ones** over three papers, at about $1.85 a paper, and no reference finding was
carried by a comment it dropped. The same gate on the macro issues did not pay
and was removed.

**The gate adds nothing to a review that was already accurate.** On the one
paper whose pipeline review was already 26 good to 6 bad, it dropped nothing
and changed no verdict. Its value depends on the paper rather than being a
uniform improvement.

**No agent-only arm beat a single well-prompted full-paper call on coverage.**
Three to twelve comments against references holding 16 and 25 findings. The
planner mattered - with it working, `psi` swarm recall went from 19% and 31% to
44% at unchanged precision - but the swarm is still below the baseline, and
sweep emitted more comments on the held-out paper (12) while matching fewer
reference findings (12%).

**The two capabilities are complementary.** The agent arms reached two `psi`
findings nothing else reached - a one-sided premise in a composition lemma, and
a curvature bound off by a factor of two - both needing a proof compared
against a lemma it invokes plus the algebra carried out. A plain prompt reached
four breadth findings the agents missed.

## Recommendation

Do not replace the staged pipeline with the swarm. The measurement does not
support it.

1. **Ship the section-selection fix.** Measured gain, no agents, no added cost.
2. **Ship `--refute` as opt-in.** It targets the measured defect and keeps the
   pipeline's coverage, at roughly $1.85 a review and a shorter report.
3. **Do not make it the default yet.** Three papers is thin, its effect was
   mis-measured three times before this, and on the one paper nobody tuned
   against it did nothing at all.
4. **Keep `--agent swarm` as an opt-in deep mode** for theory papers, where the
   appendix findings it reaches are worth the coverage it gives up. Its recall
   is the open problem.
5. **Do not turn the cross-reference round on, and do not count it out.** On
   four matched pairs it returned one reference finding, which is the size of
   the measurement's own per-pair noise, so the preregistered rule keeps it
   off. But four of its six findings were judged supported and substantive and
   only one of those was a reference item, so the recall metric the rule rests
   on cannot see most of what it produced. Deciding it needs more pairs or a
   metric that credits a demonstrated defect absent from the reference list.
   Separately: the capabilities that found deep defects here were whole-paper
   retrieval and computation inside a single agent, and that result is not in
   question.

## Caveats

- **The role prompts were written after reading the `psi` reference review, and
  name the patterns it found** (a general parameter whose proof fixes one value;
  a quantity estimated in one place and fixed in another; an error budget
  against its total; a bound controlling one coordinate where a maximum is
  needed). `psi` swarm recall is therefore in-sample. `coset_codes` is the
  held-out measurement and the prompts were not revised after seeing it.
  Precision is unaffected, being adjudicated against the paper.
- **Mostly one run per cell.** The three `psi` swarm runs span 19% to 44%
  recall, so single-run differences of that size are not evidence. The one
  exception is the cross-reference A/B, which is four matched pairs, and even
  there a pair whose second round contributed nothing still moved recall by one
  finding.
- **Two papers, one of them in-sample.** A third (`targeting`) was prepared and
  never run.
- **Both judges abstain too rarely.** Neither returned "unclear" on any claim.
  Read precision as direction, not as a rate, and hand-check a blind sample
  before any public claim.
- **The refutation gate rarely fires on agent-generated findings** (11 of 11 and
  6 of 6 confirmed). The agent arms' precision is therefore attributable to
  investigator conservatism plus whole-paper access, and the gate's own
  contribution is visible only where its input is unreliable, which is the
  paired measurement above.
- **The two references are not the same kind of document.** The `coset_codes`
  reference is an older generation and many of its items are reading
  difficulties rather than defects, which suits a breadth-first arm over one
  held to demonstration.
- **The `pipeline` arms' cost is not recorded**: they build their own client
  internally. The judge's cost reads as zero because litellm has no pricing
  entry for the judge model.
- **No hosted path.** Agent mode runs in-process against any model API so it
  works for BYOK, but it is not wired into the Modal worker or the web layer,
  and the cost gate still quotes the staged pipeline for `--agent` and
  `--refute`.
- **The sandbox does not confine the filesystem**, and denies network only
  where the host offers a mechanism.
- **The two refutation paths disagree about rewriting, and the agent path is
  the permissive one.** `agent/refutation.py`, the gate behind `--refute`, is
  purely subtractive: it never applies a refuter's `corrected_claim`, because
  applying it was measured to be the source of that stage's apparent precision
  gain, partly by retreating from an error claim to a request for
  clarification. The agent editor does apply it
  (`_render_findings_for_editor` prefers `corrected_claim` over the
  investigator's own wording). So a refuter in the agent path can still author
  review prose. The inconsistency predates the paired runs and was left alone
  rather than changed mid-experiment; it should be resolved before agent mode
  is offered to anyone, and resolving it means re-measuring the agent arms.
- **The macro-issue gate and its deletion-narrowing are gone**, removed on the
  "comments only" decision after measuring net zero. Earlier caveats about an
  English-only all-issues-refuted notice and about nobody having read a
  deletion-narrowed issue refer to that removed code and no longer apply.

## Distance from the original brief

The brief asked for agents running through Claude Code or Codex CLI, with web
search, collaborating and going back and forth until they agree. What is built
differs:

- Agents run on an in-tree tool loop against a model API, not through a
  coding-agent CLI. This is deliberate: the hosted path (Modal, BYOK) cannot
  shell out to a CLI, and that is where reviews are actually served. The
  host-CLI backend is kept behind the same interface.
- There is no web search in the agent tool set.
- Collaboration is a shared workspace plus one refutation pass. There is no
  multi-round negotiation, and agreement between agents is deliberately not
  treated as evidence.
- The goal of matching the reference reviews is not met. The best coverage
  measured here is 69% of the atomized findings on the in-sample paper and 40%
  on the held-out one.
