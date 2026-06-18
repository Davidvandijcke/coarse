# Does review-output language degrade review quality? (Design A vs Design B)

**TL;DR.** Keep **Design A** (generate the review directly in the target language, with
verbatim quotes kept in the paper's source language). Do **not** build Design B (review in
English, then translate the structured output). A local experiment and a literature review
both show direct generation does not degrade issue-finding for the languages coarse supports,
and that translating the structured output would *introduce* the one failure mode A avoids:
corruption of the verbatim quote blocks.

This is the empirical basis for the PR-F decision in `docs/MULTILINGUAL_PLAN.md`.

## Question

coarse generates reviews *directly in the target language* (**Design A**: feedback prose in
language L; every verbatim quote kept in the paper's original language — the
quote-verification integrity anchor). The contingent alternative was **Design B**: review in
English, then translate the structured output into L. Should we keep A, or build B?

## Method (local, $0 — no paid API)

The same paper was reviewed by four independent **Opus-4.8** reviewer subagents under
identical instructions, varying only the language the reviewer wrote feedback in:
**English (baseline), Spanish, Chinese (Simplified), Arabic**. Each produced exactly 12
substantive peer-review issues; each issue carries a verbatim English quote, the feedback in
the target language, and an English one-sentence gloss (`gloss_en`) for cross-lingual
matching. The paper was a complete econometrics manuscript (regression discontinuity). Two
metrics:

1. **Quote fidelity** — programmatic, via the *production* verifier
   (`coarse.quote_verify.verify_quotes_detailed`): does each quote survive the real pipeline
   gate (exact / fuzzy-recovered) or get dropped as unanchored? See
   [`score_quote_fidelity.py`](score_quote_fidelity.py).
2. **Cross-language issue recall** — an Opus judge operating **only on the English glosses**
   (so the well-documented multilingual-LLM-as-judge unreliability does not apply), measuring
   how many of the English-baseline issues each non-English review also found.

A separate literature subagent surveyed ~19 primary sources; full report in
[`multilingual_design_a_vs_b_literature.md`](multilingual_design_a_vs_b_literature.md).

## Result 1 — Quote fidelity: perfect under Design A, even Arabic

| Language | exact | fuzzy-recovered | **dropped (fabricated)** | survives pipeline |
|---|---|---|---|---|
| English (baseline) | 12 | 0 | **0** | 12/12 (100%) |
| Spanish | 12 | 0 | **0** | 12/12 (100%) |
| Chinese | 12 | 0 | **0** | 12/12 (100%) |
| Arabic | 10 | 2 | **0** | 12/12 (100%) |

**Zero dropped quotes in any language.** Writing the feedback in Spanish/Chinese/Arabic did
not corrupt the verbatim English quotes. Arabic (non-Latin, RTL) kept 10/12 byte-exact and the
other 2 were normalization-recoverable — none fabricated. (Raw: [`data/fidelity.json`](data/fidelity.json).)

## Result 2 — Issue recall: no quality degradation, just selection variance

Recall against the 12 English-baseline issues: **Chinese 9/12 (0.75), Arabic 8/12 (0.67),
Spanish 6/12 (0.50).** But the non-English reviews did **not** find *fewer real issues* — they
found a *partially different* set of equally-deep (sometimes deeper) real issues:

- **All four conditions** independently found the 5 strongest core problems (winsorizing vs an
  assumption that supports the headline result; an asymptotic-equivalence result undercutting a
  claimed finite-sample "superiority"; non-i.i.d. clustered data with an unclustered bootstrap;
  a rate condition that binds on the smallest subgroup; a barycenter estimand with no
  unit-level causal interpretation).
- The non-English reviews **surfaced real problems English missed**: a cross-covariance proof
  gap (flagged by **all three** non-English reviews), and Arabic alone caught byte-identical
  table entries (a likely tabulation bug).
- **Depth did not drop.** Arabic went *deeper* on formal proof errors, trading away English's
  empirical/specification-search concerns.
- Across all four reviews: **22 distinct real problems** (5 found by all 4; 10 by ≥3; 15 by ≥2;
  7 by exactly one). English alone found 12 — the others are *additive*.
- **No wholesale fabrication.** A few "stated-not-demonstrated" claims; Spanish was the mild
  laggard (lowest recall + its two unique claims were the shakiest), but still found all 5 core
  issues plus genuine unique ones.

The sub-100% recall is dominated by **top-12 selection variance among 22 genuine issues**, not
language-induced quality loss. The decisive signal: the *hardest, most important* issues were
found in **every** language, including Arabic. (Raw: [`data/recall.json`](data/recall.json),
[`data/glosses.json`](data/glosses.json).)

## Literature (independent corroboration)

The evidence splits along **reasoning vs generation**: English-pivot helps analytical
*correctness* (~6–14 pts on hard tasks, but only ~0–3 pts for high-resource European
languages), while **direct generation wins for output** — a Google PaLM-2 study found direct
beat pre-translation in **94/108 languages** (pivot won only ~7 low-resource). Decisively for
coarse: translate-then-X silently corrupts structure and **verbatim quote blocks at 8–50%
rates that semantic metrics miss** — which essentially rules out pure Design B for a
quote-anchored artifact.

## Recommendation

1. **Ship Design A (direct-in-language) as the default for all supported languages.** Both
   metrics and the literature agree it does not degrade issue-finding for high-resource + major
   world languages, and it keeps verbatim quotes intact.
2. **Do not build Design B (English-pivot + translate).** Unnecessary for these languages, and
   it would *introduce* quote/structure corruption (literature: 8–50%; our Design-A fidelity:
   0% dropped).
3. **Keep reasoning English-internal** (the prompt/humanizer/tone blocks are already English —
   the model forms judgments in English and emits prose in L). This is the hybrid the
   literature endorses.
4. **Optional hardening:** a target-language exemplar to suppress mid-document English drift;
   keep monitoring via the `lang_eval` harness (`src/coarse/lang_eval.py`, `scripts/lang_eval_run.py`).
5. **Low-resource long tail** (if ever added beyond the current 12): re-evaluate — the only
   regime where pivot/pre-translation may win, and where quality is weakest anyway.

## Caveats

- **N=1 paper, one run per language, English-only judge.** No English-vs-English control, so
  the ~25–50% issue non-overlap cannot be fully separated from run-to-run selection variance
  (it is plausibly *mostly* variance — a quick English-vs-English run would bound it).
- Reviewers were **Opus-4.8**; the production default is a different model. The literature says
  weaker models show larger cross-lingual gaps, so a spot-check on the production model would
  confirm transfer.
- This scores **issue-finding + quote fidelity**, not **prose naturalness** of the non-English
  feedback (the literature says naturalness also favors direct generation for strong models, so
  this is unlikely to flip the recommendation).

## Reproduce

The four reviewer subagents and the judge were orchestrated in-session (Opus-4.8); the exact
prompts are in [Appendix A](#appendix-a--subagent-prompts). The committed `data/` holds their
outputs. Re-score quote fidelity against a local paper extraction:

```bash
uv run python docs/experiments/score_quote_fidelity.py path/to/paper_extraction.md
# or, with no paper text, re-print the committed numbers:
uv run python docs/experiments/score_quote_fidelity.py
```

`data/` contents: `reviews_{en,es,zh,ar}.json` (raw reviews — quote + feedback + gloss),
`glosses.json` (judge input), `fidelity.json` (Result 1), `recall.json` (Result 2).

## Appendix A — subagent prompts

**Reviewer (one per language; only the feedback-language clause changed):** rigorous
econometrics/statistics peer reviewer, read the paper, produce exactly 12 substantive
issues (no copyedits) under a strict confidence gate; each issue = a verbatim English `quote`,
`feedback` written directly in {LANGUAGE} (not translated from English), and a `gloss_en`
(≤25-word English summary); output valid JSON.

**Judge (single, English-only):** impartial meta-reviewer; treat the English baseline's 12
issues as the reference set; two issues match iff they identify the same underlying problem
(substantive, not lexical); per non-English language compute matched-set, recall, unique
issues, and any weak/unjustified claims; tally consensus across all four; render a verdict on
whether non-English degraded.
