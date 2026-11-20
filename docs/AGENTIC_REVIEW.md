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
