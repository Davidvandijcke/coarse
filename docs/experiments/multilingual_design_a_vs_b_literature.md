# Evidence Report: Direct-in-language (Design A) vs English-pivot+translate (Design B)

(Compiled by literature-search subagent; 5 sub-topics, ~19 primary sources, independently spot-verified.)

## Bottom line

The literature splits along a fault line that maps onto the two design components —
**analytical reasoning** vs **final-prose generation** — so the honest answer is a
**hybrid, not a clean A-or-B**.

- **Reasoning/judgment** (deciding what is wrong with the paper): consistently pro-English.
  Forcing the model to *think* in the target language costs ~**6–14 accuracy points** on
  hard analytical tasks; penalty is **negligible for high-resource European (~0–3 pts)**
  and **large for low-resource/non-Latin (15–43 pts)**.
- **Final written prose**: the evidence flips. Google PaLM-2 study: generating **directly
  in the target language beat translate-via-English in 94 of 108 languages** (pre-translation
  won only for ~7 truly low-resource). "Translate-then-X" silently corrupts markdown
  structure, headings, and **verbatim quote blocks** at **8–50% rates that semantic-quality
  metrics never catch**.

So: for high-resource languages (fr, de, es, it, pt, nl, and to a lesser degree zh/ja/ko/ar
with a strong model), **Design A — direct generation — is the right default**, and a full
English-pivot-then-translate pipeline (pure Design B) is likely *worse* because it endangers
the structured artifact and verbatim quotes. Optimal: "reason in English, then **generate**
(not translate) the final review natively" + programmatic structure/quote-integrity check.
Pure end-to-end translation (B) is only worth it for genuinely low-resource targets.

## Key findings

### Pillar 1 — Cross-lingual capability gaps: small for European, large for low-resource
1. **GPT-4 / OpenAI MMMLU**: European-language gap within ~1 pt of English (o3-high: it .912 /
   es .911 / fr .906 / de .905 / pt .910). zh .893, ja .890, ko .893, ar .904, hi .898 only
   ~1–3 pts lower. Swahili .860, Yoruba .780 are the real drops. *Weaker models blow the gap
   wide open* (gpt-4o-mini: it .764 vs Yoruba .458). [simple-evals MMMLU; arXiv:2303.08774]
2. **MMLU-ProX (29 langs, 11,829 parallel items)**: Qwen3-235B (en 80.7%): fr/de/es/it/pt all
   within ±0.3pp of English; ko/ar/hi −2.0..−2.4; zh/ja −3.3..−3.6; Swahili −9.9; Wolof −43.8.
   Cleanest tier separation. [arXiv:2503.10497]
3. **Belebele (122 langs)**: frontier models hold top ~20–40 languages, then fall off a cliff.
   [arXiv:2308.16884] — your target-language LIST, not "multilingual," determines risk.
4. **Much of the historically reported gap was a translation/eval artifact.** MGSM 15–40pt gaps
   shrank to <6 (often <2) for strong models once benchmark mistranslations were fixed. Real
   gaps likely smaller than tables → *strengthens* the direct-generation case. [arXiv:2511.05162]

### Pillar 2 — English-pivot reasoning: real & large for correctness, mostly low-resource
5. **Forcing native-language *reasoning* costs 6–14 acc pts (most on-point).** XReasoning:
   R1-32B AIME 25.5→17.0 (−8.5); Skywork-32B GPQA 53.6→39.8 (−13.8). ~0 cost on easy MGSM.
   "Reasoning in English… consistently results in higher accuracy." Post-training fixes
   language-match but NOT the accuracy penalty. [arXiv:2505.22888]
6. **English reasoning beats native on MATH by 5–27 pts (up to +43 Swahili).** BUT native
   reasoning *helps* CulturalBench-Hard (+1–3%) and lowers toxicity. [arXiv:2505.17407]
7. **Self-translate to English beats direct native by ~+4.75 pts avg / 5 tasks; grows with
   model capability.** [arXiv:2308.01223, NAACL 2024]
8. **Cross-Lingual-Thought (XLT) prompting: >10 pts avg** by instructing re-express+reason in
   English; disproportionately helps weak/low-resource. [arXiv:2305.07004, EMNLP-F 2023]
9. **Mechanistic: models use English as a latent pivot** (Llama-2 concept space English-biased
   in middle layers). [arXiv:2402.10588; Cross-lingual Collapse arXiv:2506.05850]
10. **Translate-test gains concentrated in low-resource; high-resource ~tie.** MEGA/MEGAVERSE:
    >30% rel. gains for Burmese/Tamil/Telugu, ~tie for high-resource European. "Selective"
    translation beats "full English." [arXiv:2303.12528; arXiv:2502.09331]

### Pillar 3 — Generation side: direct often BEATS pivot, and translate-then-X is dangerous
11. **PaLM-2: direct generation beat pre-translation in 94/108 languages** (>5% lifts in 63%);
    pre-translation won only 7, all low-resource. Incl. generative tasks (XLSum, TyDiQA).
    *The finding that prevents a naive "always pivot through English."* [Google Research blog]
12. **Translate-then-X silently corrupts structure/formatting/quotes — semantic metrics miss it
    (biggest product risk).** EN→German docs: automated quality 94–96%, yet ChatGPT broke 50%
    of files (Claude 16%); markdown errors 24%/8%; code-block 18%/2%; URL 32%/14%. "High
    semantic quality can coexist with significant structural preservation problems."
    [arXiv:2508.02497] → **coarse implication:** `> Quote:` blocks must stay verbatim from the
    paper; round-tripping through MT breaks the quote-verification contract. **Rules out pure B.**
13. **"Language confusion": models drift to English / code-switch; instruction-tuning CAUSES it.**
    Llama-3-70B-Instruct line-level pass 46% vs GPT-4-Turbo 99.3%. Worst non-Latin. **Fix that
    works: target-language few-shot exemplar** (Command-R 1.1%→95%). [arXiv:2406.20052, EMNLP24]
14. **Instruction-following degrades + gets more variable in non-English.** M-IFEval: en ~93% →
    es ~79% → ja ~76%. [arXiv:2502.04688; Multi-IF arXiv:2410.15553]
15. **Translationese + terminology drift**: pivot output reads MT-ish and uses inconsistent
    technical terms within a doc. Native generation less prone. [arXiv:2410.15956; 2603.08450]
16. **Naturalness can be WORSE when pivoting** — strong models generate more natively directly;
    only weaker Latin-centric models benefit from the English detour. [arXiv:2410.15956; MEDAL
    arXiv:2505.22777]

### Pillar 4 — LLM-as-judge across languages (affects your EVALUATION)
17. **Judges unreliable in non-English, worst on long-form + low-resource.** κ≈0.3 avg / 25
    langs; Telugu math κ=0.002. Ensemble (majority of 3) adds ~0.15–0.25 κ. [arXiv:2505.12201]
18. **Judges systematically over-optimistic in non-English (esp. non-Latin) and prefer English
    answers.** Bias largest in humanities/social-sciences content. [MM-Eval arXiv:2410.17578;
    arXiv:2601.13649]
19. **Judging IN English ≥ native judging**, benefit largest for low-resource (Pearson 0.73 vs
    0.56). [arXiv:2605.28710] → **for your A/B test: judge in English, use an ensemble, validate
    vs a small human-rated sample per language.** Native-LLM judge will be over-lenient.

## Product decision (by tier)

| Tier | Languages | Think-in-X penalty | Direct vs pivot (generation) | Design |
|---|---|---|---|---|
| High-resource Latin | fr, de, es, it, pt, nl | ~0–3 pts | Direct ≥ pivot; pivot adds translationese, breaks structure/quotes for ~0 gain | **A (direct)**; reason in English internally |
| High-resource non-Latin | zh, ja, ko, ar, hi | ~2–7 pts | Direct wins on naturalness w/ strong model; confusion risk real | **A + strong model + target-lang exemplar + programmatic quote/structure check** |
| Low-resource | sw, yo, wo, te, bn… | 15–43 pts | Only regime where pivot may win | **B defensible**, but quality weakest regardless |

## Architecture recommendation (the hybrid the evidence supports)
1. Do analytical reasoning/judgment in English internally (strongest evidence).
2. For high-resource targets, **generate** final prose directly in the target language (don't
   translate an English review).
3. Protect invariants regardless of design: verbatim quotes from ORIGINAL paper text, never
   round-tripped through MT; target-language few-shot exemplar to suppress drift; run
   programmatic quote-verify + markdown structure check post-generation; use a frontier model.
4. If A/B testing: judge in English, ensemble, validate vs small human sample per language.

**Net:** Design B (review in English then translate the structured output) is NOT the safe
default it appears to be. For coarse's actual target languages (high-resource European + major
world languages), Design A (direct generation, English-internal reasoning, verbatim quotes) is
better on quality AND far safer for the structured/quoted format. Reserve translate-then-X for
the low-resource long tail, if supported at all.

## Caveats
- No study tests coarse's exact artifact (long structured analytical review, native vs MT).
- Two literatures point different ways; "reason in English, generate natively" is inferred.
- Largest pro-English-reasoning numbers are 2023–24 open mid-size models / R1 distills; gap
  shrinks with scale and for high-resource → frontier models likely show smaller effects.
- MT benchmarks overstate the gap → real gaps smaller → favors direct generation.
- Judge-reliability numbers are mostly self-consistency, not judge-vs-human on long-form.
