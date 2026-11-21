# Agentic review: diagnosis and design

Status: in progress on `feat/agentic-review-harness`.
Relates to #264 (bounded tools, paper context broker, evidence ledger), #270
(same-model ablation), #279 (host isolation), #260 (abstention).

## What this work is for

Reviews of theory-heavy papers miss the findings a careful referee produces, and
some of what the pipeline does produce is confidently wrong (see the Slutsky
case: a review that scored 6/6 on the quality judge and was rejected outright by
the paper's author). This document records a measured diagnosis of where the
findings are lost, then specifies the smallest harness change that could recover
them, and the evaluation that decides whether it did.

The benchmark paper for the diagnosis is *Post-Selection Inference via
Algorithmic Stability* (arXiv 2011.09462v2), chosen because a current-generation
reference review of it is available. That reference is a truncated preview: it
shows five overall issues and six detailed comments. Atomized into separate
checkable claims it yields 16 findings, recorded in
`evals/references/psi.json`.

## Diagnosis

### Every appendix proof is dropped before review

`pipeline.review_paper` filters sections, then truncates to
`MAX_REVIEWABLE_SECTIONS = 25`. On this paper `structure.analyze_structure`
returns 41 sections and the filter removes none of them, so the truncation is
what decides the review's scope. The last section reviewed is "9.2 Bernoulli
design". The 16 sections after it are never seen by any agent:

```
10 Discussion                                      1,749 chars
Acknowledgements                                  10,409
A Proofs                                               0
A.1 Composition of stability                       2,162
A.2 Proof of Claim 1                               1,845
A.3 Proof of Claim 3                                 178
A.4 Proof of Claim 2 and Claim 4                     551
A.5 Proof of Lemma 1                               1,585
<!-- PAGE BREAK -->                                1,107
A.7 Proof of Proposition 1                         5,805
A.9 Generalization and proof of Claim 5            3,487
A.10 Proof of Proposition 2 (LASSO stability)     14,263
A.12 Proof of Proposition 4 (marginal screening)   5,252
A.13 Proof of Proposition 5                        1,286
B Deferred numerical results and simulation        5,571
C Generalizations of stable algorithms             6,176
```

All six of the reference review's detailed comments are located in A.10, A.11
and Lemma 5. Three of its five overall issues depend on Appendix B, Appendix C,
or A.9. Of the 16 atomized findings, 13 require reading a section that the
current pipeline discards. No prompt revision or model upgrade can recover those
findings, because the text never reaches a prompt.

Two further structure defects compound this:

- **A.11 is not parsed as a section at all.** Its text is absorbed into A.10's
  14,263 characters. A.6 and A.8 are likewise missing, and one section is parsed
  as the literal string `<!-- PAGE BREAK -->`. Two reference findings (D4, D6)
  are located in A.11.
- **Appendix proofs are typed `other`, not `appendix`.** The
  `_MIN_APPENDIX_CHARS` filter therefore never fires on this paper, and the
  `math_content` flag rather than section type is what routes proof review.
  "Acknowledgements" absorbs the reference list and consumes 10,409 characters
  of a reviewable slot.

### The capabilities the reference findings require

Each atomized finding is tagged with what a reviewer must be able to do to
produce it:

| Capability | Findings | Share |
|---|---|---|
| Read a section the pipeline currently drops | 13 | 16 |
| Compare two separated locations in the paper | 12 | 16 |
| Carry out algebra or a numeric instantiation | 9 | 16 |
| Construct an edge case | 1 | 16 |

Cross-location comparison is the second structural gap. A section agent receives
`truncate_section(section)`, the abstract, precomputed claims and definitions,
and a notation block; it cannot retrieve any other part of the paper. The
reference findings are overwhelmingly of the form "the proof in A.10 does not
establish what Definition 2 requires", "the premise of Lemma 3(b) is one-sided",
"the displayed gradient disagrees with Algorithm 5", "Appendix B's delta exceeds
Section 9's alpha". Each needs two locations held side by side, and the current
prompt shape cannot express the second one.

Computation is the third gap. "The first upper bound is half the exact
curvature", "for n = 50 and k = 20 roughly six rows remain", "the expression is
negative despite bounding a nonnegative quantity" are all checkable by
differentiating, substituting, or evaluating. A text-only model must do this in
its head, which is exactly the regime where the Slutsky failure occurred.

## Design

Three capabilities are missing: retrieval over the whole paper, computation, and
independent verification of a candidate finding. The harness adds them as a
bounded tool runtime rather than by widening prompts.

### Workspace

One ephemeral directory per review, outside the repository and outside the user's
project:

```
paper.md              full extracted markdown
sections/NNN-slug.md  one file per parsed section
outline.md            section index with character offsets
findings/<id>.json    evidence ledger, one file per candidate finding
notes/<agent>.md      per-agent scratch space
```

The workspace is the shared medium the agents collaborate through: an
investigator writes a candidate finding as a ledger file, and a refuter reads
that file and writes its verdict beside it. Nothing in the review is carried by
conversational state between agents.

### Tools

Implemented by coarse, not inherited from a host CLI, so the same runtime works
on the hosted BYOK path where no coding-agent CLI exists:

- `paper_search(query)` — regex/substring search over the paper, returning
  matches with section and character anchors.
- `paper_read(section | anchor, before, after)` — exact passage retrieval.
- `python(code)` — subprocess with no network, a wall-clock and memory cap, and
  `sympy` available. Never executes code taken from the paper.
- `note_write(path, text)` / `finding_write(record)` — bounded writes confined to
  the workspace.
- `web_search(query)` — off by default; enabled only for the literature role.

### Roles

1. **Planner.** Reads the outline, abstract and introduction. Emits investigation
   targets: a specific question paired with the locations that bear on it.
   Targets are claim-shaped, not section-shaped, which is what lets one
   investigation span a theorem statement and its proof.
2. **Investigators**, in parallel, one per target, each with whole-paper
   retrieval and computation. Each writes zero or more candidate findings with
   verbatim anchors and any computation transcript. Zero is a valid result.
3. **Refuters**, one per candidate finding, in a fresh context that sees the
   claim and the paper but not the investigator's reasoning. The refuter must
   independently reproduce the error. A finding that is not reproduced is
   dropped. This is the mechanism the agent-swarm literature reports as the
   defense against a swarm amplifying its own confident error: verification of
   every result by a fresh agent with no shared memory of the work
   ([Gusev and Bernal Neira 2026](https://arxiv.org/abs/2609.35719), Section
   4.1). Agreement between agents that share context is not evidence.
4. **Editor.** Selects from surviving ledger entries, clusters them into overall
   issues and detailed comments, and writes nothing that is not in the ledger.

`quote_verify` and `synthesis` stay deterministic and unchanged, so the output
contract and the quote guarantee are untouched.

### Host isolation

The existing `ClaudeCodeClient` runs `claude -p --model X --output-format text`
with no isolation: ambient MCP servers, hooks, settings, skills and the caller's
working directory are all inherited. This machine's ambient MCP set includes
desktop and browser control. A paper is untrusted input, so any tool-enabled run
through a host CLI must be isolated first (#279). The flags that achieve this
while preserving subscription authentication are `--strict-mcp-config` with no
`--mcp-config`, `--setting-sources ""`, `--disable-slash-commands`,
`--no-session-persistence`, an explicit `--tools`/`--allowedTools` allowlist, and
a working directory set to the workspace. `--bare` is not usable: it forces
`ANTHROPIC_API_KEY` and so defeats the subscription path.

Host-CLI backends are therefore kept behind the same runner interface but are not
the primary path.

## Evaluation

Arms, all on one model so the harness effect is separated from a model upgrade:

0. Current pipeline, unchanged.
1. Single agent with the workspace and tools.
2. The role swarm above.
3. Minimal baseline: one full-paper prompt, no harness.

Measurement follows the rules already preregistered in #270 and #153: identical
extraction input across arms, top-K normalization so volume cannot buy recall,
precision scored by independent adjudication of every emitted comment against the
paper rather than against the reference, and at least two runs per arm to
separate effect from variance. Because the reference review for this paper is a
truncated preview, a comment that does not match it is not thereby a false
positive; precision comes from adjudication, not from absence.

Decision rule, fixed before the results are read: if arm 1 matches arm 2, the
swarm is unnecessary and only the workspace and tools ship. If arm 0 with a
frontier model matches both, the harness change is not what was missing and the
section-truncation fix carries the gain on its own.

## Measured results

Two papers, one model (`anthropic/claude-opus-5.5` via OpenRouter), one
extraction per paper shared by every arm, top-20 comment normalization. Recall
is scored against the atomized reference findings. Precision adjudicates every
claim a review makes — detailed comments and macro issues alike — against the
paper itself, by a judge from a different model family
(`openai/gpt-5.6-terra-pro`) so no model grades its own prose.

`psi` is the paper the diagnosis was done on. `coset_codes` is held out; see the
leakage caveat, which is the reason it exists.

### psi (16 reference findings)

| arm | comments | issues | recall | precision | of which comments | unsupported | cost | time |
|---|---|---|---|---|---|---|---|---|
| pipeline, before the section fix | 21 | 11 | 56% | 52% | 60% | 15 of 32 | n/a | 442s |
| pipeline, after the section fix | 25 | 11 | **69%** | 68% | 70% | 10 of 36 | n/a | 504s |
| pipeline + `--refute` | 16 | 12 | 56% | 79% | **94%** | 6 of 28 | n/a | 567s |
| baseline, one full-paper prompt | 14 | 5 | 56% | 95% | 93% | 1 of 19 | $0.65 | 166s |
| single agent with tools | 6 | 4 | 25% | 100% | 100% | 0 of 10 | $1.05 | 492s |
| swarm, structural targets | 7 | 4 | 19% | 100% | 100% | 0 of 11 | $2.09 | 547s |
| swarm, structural targets | 6 | 5 | 31% | 100% | 100% | 0 of 11 | $3.38 | 772s |
| swarm, planner working | 9 | 4 | 44% | 100% | 100% | 0 of 13 | $2.98 | 814s |
| sweep | 7 | 4 | 25% | 100% | 100% | 0 of 11 | $5.09 | 949s |

### coset_codes, held out (25 reference findings)

| arm | comments | issues | recall | precision | of which comments | unsupported | cost | time |
|---|---|---|---|---|---|---|---|---|
| pipeline | 19 | 12 | **40%** | 48% | 58% | 16 of 31 | n/a | 546s |
| pipeline + `--refute` | 14 | 11 | 32% | 72% | **100%** | 7 of 25 | n/a | 592s |
| baseline, one full-paper prompt | 20 | 6 | 20% | 96% | 100% | 1 of 26 | $1.06 | 290s |
| swarm, structural targets | 3 | 3 | 8% | 83% | 100% | 1 of 6 | $2.06 | 731s |
| sweep | 12 | 5 | 12% | 94% | 92% | 1 of 17 | $3.93 | 738s |

### A second, stronger adjudication

The judge above answers from one prompt holding the whole paper, and it never
returned "unclear" on roughly 170 claims, which is not credible calibration. It
is also being asked to do what the harness exists to do — look a definition up,
re-derive a step, check whether an objection is answered elsewhere — without the
means. `evals/adjudicate.py` re-runs the audit with a judge that has the same
workspace and tools the agents get.

It is **more lenient** than the single-prompt judge, so the single-prompt
precision figures above are too harsh:

| run | single-prompt judge | tool-using judge |
|---|---|---|
| `coset_codes` pipeline (same 16 claims) | 48% | 69% |
| `psi` swarm, planner working (13 claims) | 100% | 92% |

The direction survives and the gap narrows. What the stronger judge establishes
much more firmly is the *mechanism*: of the six unsupported claims it found
across both runs, **five are objections the paper answers elsewhere**, and it
names the location each time — "answered in Section 8.2", "answered in Section
II.E, immediately following the redundancy definition", "answered in Section
I-B". Even the agent arm's single failure is of that kind.

## What the numbers say

**The section truncation was real and fixing it helped.** Reviewing the
appendices took `psi` recall from 56% to 69% and precision from 52% to 68%. This
is the cheapest change here and it needs no agents.

**The staged pipeline's defect is precision, not coverage.** It is the coverage
leader on both papers and also asserts the most claims the paper does not
support. The failure has one cause, now confirmed by a judge that checked: the
objection is answered in a part of the paper a section agent cannot see.

**Independent refutation fixes it at the point it matters.** Adding `--refute`
to the staged pipeline took detailed-comment precision from 58% to 100% on the
held-out paper and from 70% to 94% on the other, dropping three and four
comments respectively. The refuter's reasons are the right ones: "I read the
passage in §8.1. The sentence is conditional", "the paper does make the
full-rank assumption only for the selected model".

**The precision still missing is entirely in the macro issues.** After
refutation, detailed-comment precision is 94% and 100% while macro-issue
precision is 58% and 36%. The stage only refutes detailed comments. Extending
it to the overall feedback is the obvious next change, and the measurement says
it is where the remaining false criticism lives.

**The agent-only arms under-cover.** Three to twelve comments against references
holding 16 and 25 findings. The planner mattered: with it working, `psi` swarm
recall went from 19% and 31% to 44% at unchanged precision. Sweep did not fix
coverage — it emitted more comments on the held-out paper (12) but matched fewer
reference findings (12%), finding real but different things. No agent-only arm
beat a single well-prompted full-paper call.

**The two capabilities are complementary.** The agent arms reached two `psi`
findings nothing else reached — a one-sided premise in a composition lemma, and
a curvature bound off by a factor of two — both needing a proof compared against
a lemma it invokes plus the algebra carried out. A plain prompt reached four
breadth findings the agents missed.

## Recommendation

Do not replace the staged pipeline with the swarm. The measurement does not
support it.

1. **Ship the section-selection fix.** Measured gain, no agents, no added cost.
2. **Ship `--refute`.** It targets the measured defect and keeps the pipeline's
   coverage, at one agent call per surviving comment.
3. **Extend refutation to the macro issues.** All the remaining unsupported
   claims are there. Small change, and the evidence for it is in the table.
4. **Keep `--agent swarm` as an opt-in deep mode** for theory papers, where the
   appendix findings it reaches are worth the coverage it gives up. Its recall
   is the open problem.

## Caveats

- **The role prompts were written after reading the `psi` reference review, and
  name the patterns that review found** (a general parameter whose proof fixes
  one value; a quantity estimated in one place and fixed in another; an error
  budget against its total; a bound controlling one coordinate where a maximum
  is needed). `psi` swarm recall is therefore in-sample. `coset_codes` is the
  held-out measurement and the prompts were not revised after seeing it.
  Precision is unaffected, being adjudicated against the paper.
- **Mostly one run per cell.** The three `psi` swarm runs span 19% to 44%
  recall, so single-run differences of that size are not evidence.
- **Both judges abstain too rarely.** Neither returned "unclear" on any claim.
  Read precision as direction, not as a rate, and hand-check a blind sample
  before any public claim.
- **The refutation gate rarely fires on agent-generated findings** (11 of 11 and
  6 of 6 confirmed). So the agent arms' precision is attributable to
  investigator conservatism plus whole-paper access, and the gate's independent
  contribution is only visible where its input is known to be unreliable — which
  is the `pipeline_refuted` arm, where it fires and works.
- **The two references are not the same kind of document.** The `coset_codes`
  reference is an older generation and many items are reading difficulties
  rather than defects, which suits a breadth-first arm over one held to
  demonstration.
- **The `pipeline` arms' cost is not recorded**: they build their own client
  internally. The judge's cost reads as zero because litellm has no pricing
  entry for the judge model.
- **No hosted path.** Agent mode runs in-process against any model API so it
  works for BYOK, but it is not wired into the Modal worker or the web layer.
  The host-CLI backend is unusable until `claude login` is re-run.
- **The sandbox bounds resources and network, not the filesystem.** A real
  filesystem jail needs OS-level isolation and is not implemented.
