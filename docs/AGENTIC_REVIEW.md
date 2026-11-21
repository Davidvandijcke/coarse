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
  every comment that survives the editorial filter to a refuter.
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

**Figures withdrawn pending re-measurement against the final code.** Three
earlier attempts at this number were wrong in instructive ways, and the
mistakes are recorded here because each of them would have shipped a false
claim:

1. **Comparing a `pipeline_refuted` run with a `pipeline` run.** Two different
   reviews, so nothing was attributable to the gate.
2. **Scoring a post-refutation review end to end.** That re-judges claims the
   gate left untouched, and the judge drifts: the arithmetic did not close, and
   at least one byte-identical claim flipped verdict between scorings. Fixed by
   carrying stored verdicts forward and judging only changed text.
3. **Scoring "is this claim supported by the paper?" alone.** The gate was
   rewriting comments as well as dropping them, and some rewrites retreated
   from "X is wrong" to "the paper does not say how X was handled". That
   satisfies the supported test while giving the author less, so the metric was
   rewarding a hedge. Reading the saved reviews also showed every narrowed
   issue body had come back *longer* than the one it replaced, each prefixed
   with the issue title.

The third finding changed the design rather than the measurement. The gate is
now purely subtractive: comments are kept or dropped and never rewritten, and
an issue is narrowed only by deleting verbatim spans the refuter names, so
every surviving word is the reviewer's own. `evals/refute_effect.py` measures
it on identical generation, carrying stored verdicts forward for unchanged
claims, and reports good and bad claim counts under both "supported" and
"supported and substantive".

The general shape that survived all three attempts: the gate removes some false
criticism and costs some true criticism, the trade looked favourable on both
papers, and it costs roughly $2 a paper. The magnitude is what was unreliable,
and one run also sits inside the refuter's own variance — repeated on identical
input it has dropped 4, 5 and 6 of the same comments.

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

**Independent refutation removes some of it, at a cost in coverage.** The size
of the effect is being re-measured against the final code; see above for why
three earlier figures were withdrawn.

**Refuting the macro issues matters as much as refuting the comments.** With
comments alone refuted, macro-issue precision lagged badly and held total
precision down, because the overall feedback was never checked. An issue is
rarely wholly wrong, so it is narrowed by deleting the spans the paper answers
rather than dropped whole.

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
   pipeline's coverage, at roughly $2 a review and a shorter report. Both
   halves of the review are checked.
3. **Do not make it the default yet.** Its effect has been mis-measured three
   times, and one run sits inside the refuter's own variance. Changing a
   default needs the effect size on more papers with repeats per cell.
4. **Keep `--agent swarm` as an opt-in deep mode** for theory papers, where the
   appendix findings it reaches are worth the coverage it gives up. Its recall
   is the open problem.

## Caveats

- **The role prompts were written after reading the `psi` reference review, and
  name the patterns it found** (a general parameter whose proof fixes one value;
  a quantity estimated in one place and fixed in another; an error budget
  against its total; a bound controlling one coordinate where a maximum is
  needed). `psi` swarm recall is therefore in-sample. `coset_codes` is the
  held-out measurement and the prompts were not revised after seeing it.
  Precision is unaffected, being adjudicated against the paper.
- **Mostly one run per cell.** The three `psi` swarm runs span 19% to 44%
  recall, so single-run differences of that size are not evidence.
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
