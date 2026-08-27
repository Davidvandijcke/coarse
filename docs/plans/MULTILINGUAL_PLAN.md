# Multilingual Support — Finishing Plan (v2, adversarially reviewed)

> Status: PROPOSED. Supersedes `docs/I18N_ROLLOUT_BACKLOG.md` (written
> 2026-04-13, now partially overtaken by `dev`). Reflects `origin/dev` as of
> 2026-06-17. Every codebase claim below was verified against source; v2
> additionally folds in three adversarial reviews (technical/quality,
> release/ops, product/UX).

## 0. TL;DR

The multilingual work is **~1 PR deep and stranded**. "PR-1 (schema + API
contract)" was written but is **uncommitted** in a sibling worktree
(`../coarse-i18n-backlog`, branch `codex/i18n-01-schema-contract`) pinned to a
**~113-commit-stale** dev point. Nothing is committed, staged, stashed, or
pushed — if that worktree is cleaned, the work is gone. The other 6 PRs exist
only as a planning doc + four **empty** placeholder branches.

Since the plan was written, `dev` independently shipped **`result_json`** (a
jsonb dump of the `Review` model, read by the web UI), which **duplicates
PR-1's `review_json`** and delivers most of the old "PR-3". The plan must be
reconciled, not executed verbatim.

**The product goal that drives the sequencing:** a paper submitted in language
X gets, with zero configuration, a review written **in language X**, with the
verbatim quotes left in the source language and the analysis quality protected.

**Approach: build fresh on current `origin/dev`.** The stranded PR-1 is ~176
lines of mostly-boilerplate schema/contract on a 113-stale base; the
corrections rewrite most of it (drop `review_json`/`taxonomy`, flip the default,
fix the validators) and the largest work (de-English-ifying the analysis) is
greenfield. So we do not rebase or "rescue" the branch — we snapshot its diff
for reference and write PR-A clean on dev, informed by its design.

**Corrected execution order** (two inversions fixed vs the old plan):
```
Step 0 (snapshot stranded diff for reference — optional, ~2 min)
  → PR-A  schema + contract, reconciled AND wired to the worker
  → PR-B  detection + language threading + localized review (MVP, design A)   [split package/web]
  → PR-C  de-English-ify the analysis (structure typing, garble, tokens, quotes, literature)
  → PR-D  JSON-first rendering (finish what result_json started)   [precedes label localization]
  → PR-E  localize synthesis labels + the 2 transactional emails
  → PR-F  early eval → decide analysis-language policy (measures A; gates B)
  → [PR-G] English-pivot localization (design B) — only if PR-F demands it
  → PR-H  site UI i18n (lowest priority; RTL descoped from v1)
```

## 1. Ground truth (verified)

### 1.1 What exists (stranded)
- Uncommitted **PR-1** in `../coarse-i18n-backlog`: `LanguageContext`
  (`src/coarse/types.py`), TS mirror + `Review`-interface fields
  (`web/src/lib/types.ts`), 7 columns + 3 indexes (`deploy/supabase_schema.sql`),
  idempotent migration (`deploy/migrate_i18n_contract.sql`), and
  accept/normalize/validate of language fields in
  `web/src/app/api/{submit,mcp-finalize,review/[id]}/route.ts`.
- Untracked `docs/I18N_ROLLOUT_BACKLOG.md` (the original 7-PR plan).
- Four empty branches, 0 commits ahead of dev.

### 1.2 What `dev` already has (overtakes the old plan)
- **`result_json jsonb`** on `reviews` (`migrate_result_json.sql`), written by
  `modal_worker._review_result_json()` (`model_dump_json()` of `Review`),
  consumed by the web UI (`ReviewPageClient.tsx:401`, `ReviewDisplay.tsx`,
  `review/[id]/route.ts:28`) with markdown fallback for legacy rows.
- **`taxonomy`** column already on `reviews`.
- **`deploy/mcp_server.py` is RETIRED** (v1.3.0). The live finalize path is
  `web/src/app/api/mcp-finalize/route.ts`.
- `dev` is ~9 commits ahead of `main` with un-shipped `src/coarse/` work
  (`cli_review.py`, SKILL.md) — the multilingual package PRs will stack on top
  (release implications, §6).

### 1.3 English-assumption hotspots (verified against source)
| # | Hotspot | Evidence | Effect on non-English |
|---|---------|----------|------------------------|
| H1 | `garble.py` Latin-script bug | `GARBLE_CHARS` flags `®/õ/È/À/Á` (`garble.py:10-15`); `_GARBLE_REPLACEMENTS` does `®→fi`, `naõÈve→naïve` (`:30-41`); `normalize_ocr_garble` runs **unconditionally** in extraction (`extraction.py:212`) | Romance text corrupted; inflated `garble_ratio` auto-triggers extraction QA |
| H2 | Section typing English-only, **no LLM fallback** | `_TYPE_KEYWORDS` (`structure.py:32-58`), `_classify_section_type` (`:247`) returns `OTHER` for non-matches; math typing *does* have an LLM fallback (`_detect_math_sections`) | Every section → `OTHER`: references reviewed (`pipeline.py:479`), lit-routing + cross-section silently off |
| H3 | 13 hardcoded English labels | `synthesis.py:43-88` | Headers stay English under localized feedback |
| H4 | Token estimate `len//4` | `extraction.py:230-231`, feeds `cost.py` + `estimate_section_count` (`pipeline_spec.py:84-89`) | CJK under-quoted ~4-6×; user approves low, pays more |
| H5 | Quote candidate pre-filter `.split()` | `quote_verify.py:203-205`; top-K Jaccard (`_JACCARD_TOP_K=5`) | Spaceless CJK: degenerate Jaccard can **drop** a valid quote, not just slow it |
| H6 | `min_length=20` on quote | `types.py:216-219` (Pydantic) | 20 CJK chars ≫ 20 English; valid CJK quotes fail validation → instructor retries/fails |
| H7 | English steering blocks | `_TONE_BLOCK` (`prompts.py:27-36`), `_HUMANIZER_BLOCK` (`:38-54`) — an **English-vocabulary blocklist** + English style rules; concatenated into overview/section/completeness/editorial system prompts; editorial STEP 6 rewrites feedback against it (`:2059-2065`) | Under design A these fight "write in French" and apply an English rubric to French/Chinese prose |
| H8 | English literature context injected everywhere | Perplexity output (English, `PERPLEXITY_SYSTEM`) injected into overview (`pipeline.py:562`) and **every** section agent (`:610`); arXiv fallback English-dominated | Re-injects English into localizing agents; surfaces Anglophone lit for non-English traditions |
| H9 | Extraction-QA vision prompt English-only | `EXTRACTION_QA_SYSTEM`; find-replace `_apply_corrections` (`extraction_qa.py`) | More error-prone reproducing non-Latin substrings; auto-triggers more often (via H1) |
| H10 | `author_notes` plumbing (NOT a bug — the template) | `prompts.author_notes_block` (`:254`), threaded through `review_paper`→`review_stages`→6 agents; empty path is genuinely byte-identical | A `language` arg follows the identical path |

### 1.4 User-facing language surfaces (the full map — old plan covered only the pipeline)
- **Generation pipeline:** the 6 output agents + structure + synthesis (covered).
- **Submission → worker:** `submit/route.ts` Modal trigger body, `ReviewRequest`,
  `review_paper()` — language must be threaded and the **effective review_language
  resolved in the worker after detection**.
- **Subscription handoff:** `web/src/lib/mcpHandoff.ts` `buildAgentPrompt` +
  `buildCliCommands`, the `/h/<token>` bundle, `/api/cli-handoff`, and the bundled
  `src/coarse/_skills/*/SKILL.md` — the agent's instruction set. **Currently
  carries no language.**
- **Post-review discussion:** per-comment chat (`web/src/lib/openrouterChat.ts`)
  and "Discuss with your AI" (`web/src/lib/aiHandoff.ts`) — both English-only.
- **Transactional text:** confirmation email (`submit/route.ts:394-405`),
  completion email (`modal_worker.py:892-899`), status page
  (`status/[id]/page.tsx`), error strings — all English.
- **Read/render:** `web/src/lib/parseReview.ts` keys off literal English
  `## Overall Feedback` / `## Detailed Comments` / `**Status**:` / `**Quote**:`
  / `**Feedback**:` — localizing those headers breaks the parser (§4 PR-D/PR-E).
- **CLI:** `coarse review`, `coarse-review`, `--help`, README — no `--language`.
- **Eval/compare:** `web/src/app/compare/page.tsx` LLM-judge is English-prompted.

## 2. The central design decision: where does localization happen?

- **A — generation-time instruction (single pass).** Inject a language
  directive into each agent so it writes feedback **directly** in
  `review_language`; quotes stay verbatim source-language. Minimal surface
  (mirrors `author_notes`, H10), no extra LLM stage, end-to-end immediately.
- **B — English-pivot + post-pass localization.** Agents reason/write English
  (canonical); a new `localization.py` translates only human-facing fields
  afterward. Keeps analysis canonical but adds a whole LLM stage with its own
  cost and failure modes.

**Recommendation: ship A as the MVP; let PR-F (an early eval) decide whether B
is needed, and for which languages.** Rationale: B strictly adds LLM passes, and
coarse has a documented "confident-but-wrong" failure mode (memory
`feedback_slutsky_false_depth`) that more passes can amplify. A is a fraction of
the surface and delivers the value now.

**But A is not free, and (correcting v1) it is *not* automatically "safer":**
- A asks each agent to reason **and** emit a non-English critique in one pass —
  added load on exactly the step (proof verification, `verify.py`) the pipeline
  already fails at. Do **not** assume A protects math quality; PR-F must measure
  it, split by section type, and we may **hold proof/verify sections to English
  reasoning** even when prose localizes.
- A fights the English steering blocks (H7) and English literature context (H8)
  baked into every agent message. The language directive must therefore
  **neutralize/replace** the `_HUMANIZER_BLOCK`/`_TONE_BLOCK` rules when
  `review_language != en`, and we should reconsider injecting English lit context
  into localizing agents. Treating localization as "just prepend a sentence"
  (the old framing) underestimates this.
- A risks the model "helpfully" translating a quote → the quote fails the
  source-text verifier → the comment is **silently dropped** → recall degrades
  for non-English papers specifically. PR-F must measure the **comment drop
  rate**, and the directive + editorial/repair prompts must reinforce
  "quotes stay source-language."

## 3. Reconciliation decisions (apply before any code)

1. **Drop `review_json`; reuse `result_json`.** Embed language + new structured
   fields into the `Review`/`DetailedComment` Pydantic models so
   `model_dump_json()` carries them into `result_json` for free. After PR-A,
   `grep -rn review_json` must be empty.
2. **Drop the duplicate `taxonomy` SQL column** (dev has it); keep the TS
   `Review`-interface `taxonomy` addition (dev's TS lacks it).
3. **Delete `deploy/mcp_server.py` from all file lists** (retired).
4. **Build PR-A fresh on a branch off current `dev`** — do NOT rebase or
   cherry-pick the stale worktree (4/7 files drifted hard; `submit/route.ts`'s
   catch-block was *inverted* by a prod fix — a naive merge could reintroduce
   the `OPENROUTER_API_KEY=MISSING` bug). Write the contract greenfield against
   dev's current files, using the snapshot (Step 0) only to crib the locale
   edge-cases — and **fix** the validators while you're at it (the BCP-47 casing
   bug, §3.6), rather than porting them verbatim.
5. **Default `review_language` to the detected paper language, not site
   language.** Zero-config path = "review my paper in its own language."
   Resolution `review_language = explicit ?? detected_paper_language ??
   site_language ?? "en"` happens **in the worker after extraction/detection**
   (paper_language is unknown at submit time). `LanguageContext.review_language`
   loses its hardcoded `"en"` default (empty = "follow paper").
6. **Inject a language NAME, not a code, into LLM prompts.** Build one
   `code → human name` catalog ("fr"→"French", "zh-Hant"→"Traditional Chinese")
   as a single source of truth (`src/coarse/languages.py` + a TS mirror), reused
   by the directive, the label catalog (PR-E), and the picker (PR-H). Fix the
   BCP-47 casing bug: stop lowercasing script/region subtags (`zh-Hant`, not
   `zh-hant`); canonicalize against the catalog.
7. **Detect language in an isolated step, NOT by extending the metadata call.**
   Folding a `language` field into `PaperMetadata`/`_get_metadata` would change
   the metadata prompt + JSON schema on **every** run and risks the
   `max_tokens=512` truncation cliff (`structure.py:326-330`) → silently
   downgrades English reviews. Instead: a cheap script+stopword heuristic in
   `src/coarse/languages.py` (LLM tiebreak only when ambiguous), run on a
   **body sample** (not just the title page — CJK journals have English
   abstracts over CJK bodies). This preserves the byte-identical-default
   invariant honestly.
8. **Defer `analysis_language`.** Under design A it has no reader (speculative
   config, against CLAUDE.md's "no flexibility that wasn't requested"). Keep it
   as a reserved/inert column; activate only if PR-G (design B) is built.
9. **Descope RTL from v1.** Support LTR languages (CJK, Cyrillic, Romance,
   etc.) first. Mixed LTR-math/LTR-quotes inside RTL prose in a markdown doc is
   genuinely broken and needs per-segment direction + bidi isolates — a
   dedicated effort, not a `dir="rtl"` checkbox. Say so explicitly rather than
   implying RTL is covered.

## 4. PR stack (re-sequenced, re-scoped)

Each PR is additive, preview-validated, and rebased onto latest `dev` before
merge. Sizes are honest (v1 under-sized several).

### Step 0 — SNAPSHOT for reference (optional; ~2 min)
We are **not** rescuing/rebasing the stranded branch — PR-A is greenfield. The
only value left in the worktree is the original author's tested locale
edge-cases, worth keeping handy while writing the new validators:
```bash
git -C "../coarse-i18n-backlog" diff > /tmp/i18n_pr1_reference.patch
```
This file is reference-only; nothing depends on it. Track this plan
(`docs/MULTILINGUAL_PLAN.md`) and, for provenance, the original
`docs/I18N_ROLLOUT_BACKLOG.md` on the working branch.

### PR-A — Schema + contract, reconciled AND wired to the worker (small–medium)
The corrected PR-1, made *functional* (v1's PR-A stranded data in a column).
- **Files:** `deploy/supabase_schema.sql`, `deploy/migrate_i18n_contract.sql`,
  `src/coarse/types.py`, `web/src/lib/types.ts`,
  `web/src/app/api/{submit,mcp-finalize,review/[id]}/route.ts`,
  **`deploy/modal_worker.py`** (`ReviewRequest.review_language` etc.),
  and the `submit→Modal` trigger body.
- **Do:** add the 5 functional language columns (`site_language`,
  `review_language`, `paper_language`, `paper_language_source`, `text_direction`)
  + reserved-inert `analysis_language` + indexes — **NOT `review_json`** (reuse
  `result_json`), **NOT `taxonomy`** (exists). Add `LanguageContext` (Python +
  TS) with `review_language` defaulting to empty (§3.5). **Union** the read
  SELECT (keep `result_json`! the stranded SELECT omits it — a naive port breaks
  every review). Accept/normalize/validate language fields (port validators
  verbatim, fix BCP-47 casing §3.6). Thread `review_language` from submit → Modal
  body → `ReviewRequest` so the contract reaches the worker (resolution happens
  in PR-B).
- **Migration safety:** additive + idempotent, no backfill; mirror
  `migrate_result_json.sql`'s deploy-order note (apply to preview Supabase
  **before** the web deploy that SELECTs new columns, else Postgres 42703);
  consider `create index concurrently`.
- **Acceptance:** existing submissions byte-identical when fields unset; old +
  new rows load; `result_json` render + comment chat still work (preview smoke).
  Tests: `tests/test_types.py` (`LanguageContext` defaults); a
  `test_web_security_invariants.py`-style invariant test asserting the validator
  rejects malformed codes and accepts the BCP-47 cases.
- **Risk:** low–medium. Landmine = the SELECT union and the `review_json`→
  `result_json` scrub.

### PR-B — Detection + threading + localized review (the MVP, design A) (LARGE — split)
The value-delivering milestone. Split across the PyPI/web boundary so it ships
atomically on each side (§6).

**PR-B1 (package — ships via PyPI):**
- `src/coarse/languages.py` (NEW): code↔name catalog (§3.6) + isolated
  detector (§3.7, body-sample, heuristic+LLM-tiebreak).
- `src/coarse/prompts.py`: `language_instruction_block(language_name)` that (a)
  instructs target-language output, (b) **keeps quotes verbatim source-language**,
  (c) keeps LaTeX unchanged, and (d) **neutralizes `_HUMANIZER_BLOCK`/`_TONE_BLOCK`
  when non-English** (H7).
- Section-typing fix moved EARLY (foundational for non-English to work at all):
  language-aware `_classify_section_type` — **keyword-first** (English
  determinism preserved), LLM map only for `OTHER` headings; English regression
  test asserting identical types on English fixtures.
- Thread `language` through `pipeline.review_paper(language=...)` →
  `review_stages` → the 6 output agents, exactly like `author_notes` (H10).
- `config.py` `review_language`; `cli.py` + `cli_review.py` + `headless_review.py`
  `--language`; `_skills/*/SKILL.md` (honor language; forbid quote translation).
- Make `min_length=20` script-aware (H6) so CJK quotes validate.
- Reinforce "quotes stay source-language" in `EDITORIAL_SYSTEM` +
  `QUOTE_REPAIR_SYSTEM`.

**PR-B2 (web/worker — ships via Modal/Vercel):**
- `modal_worker.py`: run detection, resolve effective `review_language` (§3.5),
  pass to `review_paper`, persist detected `paper_language` +
  `paper_language_source`.
- `web/src/app/page.tsx`: ship the `review_language` **picker now** (default
  "follow paper"), so PR-B doesn't deliver localization with no user control.
- Thread language to the **subscription handoff**: `mcpHandoff.ts`
  `buildCliCommands` (`--language`), the `/h/<token>` bundle, `buildAgentPrompt`
  context.
- Thread to **discussion surfaces**: `openrouterChat.ts` + `aiHandoff.ts`
  ("respond in {name}").
- Surface detected language + an override on the review page
  (`ReviewDisplay`/`ReviewPageClient`) so wrong detection is visible/correctable
  (`paper_language_source` is otherwise write-only).
- Show a one-line quality note when `review_language != en` (the confident-wrong
  mode worsens off-English).
- Recompute the cost estimate when language changes (H4 makes CJK pricier).
- README + `--help` document `--language`.
- **Acceptance:** a Chinese/Spanish/French paper, **no language set**, yields a
  review whose prose is in the paper's language, quotes source-language and
  verifying; default (no language, English paper) **byte-identical** (golden-file
  test, §6); end-to-end **preview smoke** (submit→preview Modal→render localized).
- **Risk:** high surface, mechanical core. The byte-identical golden test + the
  drop-rate watch are the guardrails.

### PR-C — De-English-ify the analysis (medium)
Make non-English *analysis* correct (PR-B made the *output language* work; this
makes the pipeline reason about non-English input properly). Independent files →
can run parallel to PR-D/PR-E.
- **Do:** H1 garble fix (stop flagging/replacing legitimate accented Latin;
  gate `_GARBLE_REPLACEMENTS`); H4 script-aware token estimate (Python +
  `web/src/lib/estimateCost.ts` + regenerate `pipelineSpec.json`); H5 script-aware
  quote candidate **selection** (char-n-gram windows or bounded `SequenceMatcher`,
  not degenerate Jaccard); H8 pass language to `literature.py`/`PERPLEXITY_SYSTEM`
  and reconsider English-lit injection into localizing agents; H9 language-aware
  `EXTRACTION_QA_SYSTEM` + drop unmatched corrections; non-English math keywords
  (cheap add; LLM fallback already covers the rest).
- **Acceptance:** English byte-stable (regression fixtures); ≥1 Romance + ≥1 CJK
  paper pass smoke with correct references exclusion, section typing, quote
  survival, and cost estimate within X% of actual.
- **Risk:** medium — garble + token + section-typing changes touch the English
  path; guard with English regression tests.

### PR-D — JSON-first rendering (medium — a real build, NOT "already done")
Finish what `result_json` started so localization rides structured data, not
markdown string-parsing. **Must precede PR-E** (label localization), because the
web is markdown-**first** today (`parseReview` returns null if it can't find the
English headers → raw dump).
- **Do:** make `ReviewDisplay`/`ReviewPageClient` render **primarily from
  `result_json`** (markdown fallback = legacy only); embed `LanguageContext` (+
  `dir`) and `quote_original`/`quote_translation` on the models so they flow into
  `result_json`; emit a JSON sidecar on the **CLI** paths (`cli.py`,
  `cli_review.py`, `headless_review.py` currently write markdown only — net-new).
- **Acceptance:** new reviews render from `result_json` incl. language; legacy
  markdown still renders; CLI emits both. Golden-file byte test for the markdown
  path stays green.
- **Risk:** medium (core render path).

### PR-E — Localize synthesis labels + transactional emails (small–medium)
- **Do:** replace `synthesis.py`'s 13 labels with a `review_language`-keyed
  catalog (reuse §3.6 names; English fallback). **Keep the machine-readable
  structural markers stable** (`## Overall Feedback`, `## Detailed Comments`,
  `**Status**: [Pending]`, `**Quote**`, `**Feedback**`, `**Filter**`) OR rely on
  PR-D's json-first render and downgrade markdown-parsing to legacy — pick one
  and verify `parseReview.ts` + `compare/page.tsx` + any refine.ink interop.
  Localize the **two emails** (highest-visibility non-review text) using the
  `review_language` already on the row.
- **Acceptance:** localized reviews render localized prose; English unchanged;
  web parser + compare page don't break.
- **Risk:** low–medium (string-parser blast radius — that's why PR-D precedes).

### PR-F — Early eval → decide analysis-language policy (medium; dev-only) — PULLED FORWARD
Was the old PR-7 (last). Runs **after PR-C** (so non-English papers parse
correctly) and **before** committing to skip design B.
- **Do:** on a fixed set (English + ≥2 non-English incl. ≥1 CJK, ≥1 Romance),
  compare **A vs B** on issue recall, **comment drop-rate**, false-positive rate,
  quote fidelity, translation adequacy — **split by section type** (prose vs
  proof). Reuse `quality.py`/`recall.py`.
- **Acceptance:** a written, numbers-backed `analysis_language` policy. If A
  holds → skip PR-G. If A degrades for some languages/section-types → build PR-G
  narrowly (e.g. English reasoning for proofs only).
- **Risk:** low; high de-risking value.

### PR-G — (contingent) English-pivot localization (design B) (large)
Only if PR-F demands it. `src/coarse/localization.py` post-pass translating
human-facing fields; English canonical reasoning; quotes untouched; activates
`analysis_language`. Build narrowly for the languages/section-types the eval
flagged.

### PR-H — Site UI i18n (large) — LOWEST PRIORITY
Translating UI chrome is unbounded and lower-value than localizing the review.
`LanguagePicker` is already shipped (in PR-B) for review_language; PR-H adds
static-string localization, `<html lang>` dynamic, a small supported-locale set.
**RTL is a separate, explicitly-scoped effort** (§3.9), not folded in here.

## 5. Dependency notes (why this order)
- **PR-D before PR-E:** localizing labels before json-first rendering breaks the
  English-string markdown parser for every non-English review.
- **PR-C before PR-F:** evaluating A vs B on a mis-sectioning pipeline measures
  noise, not the localization choice.
- **Section-typing fix lives in PR-B**, not PR-C: it's the floor for any
  non-English review working at all.
- PR-C ∥ PR-D ∥ PR-E touch mostly disjoint files and can overlap once PR-B lands.

## 6. Cross-cutting invariants (must hold for every PR)
- **Default path byte-identical.** Language unset ⇒ output identical to today.
  Enforced by a **committed golden-markdown fixture + byte-equality test**
  asserted from PR-B onward (this is the single highest-value test; v1 hand-waved
  it). Detection is isolated (§3.7) so the metadata call is untouched.
- **Quotes are never translated.** `quote_original` stays verbatim
  source-language; verification runs on source text only. The integrity anchor —
  reinforce in the directive + editorial + repair prompts, and **measure the
  drop rate** (a translated quote silently drops the comment).
- **PyPI/web split-ship.** `src/coarse/` changes ship via tag-driven PyPI
  release; web/deploy via Vercel/Modal. Keep package and web halves in separate
  PRs (PR-B1/PR-B2) and gate the user-visible feature so it only "turns on" when
  *both* halves have shipped. Note the existing 9-commit `dev`-ahead-of-`main`
  backlog so the release manager doesn't tag multilingual mid-flight.
- **Preview-first** for every web/schema/worker/pipeline PR; migrations additive
  + idempotent + applied to preview before the deploy that reads them.
- **No model IDs outside `models.py`; prompts only in `prompts.py`.**

## 7. Decisions

**Resolved (2026-06-17):**
1. **Localization design:** ✅ A as MVP (write directly in target language),
   B only if PR-F's eval demands it; possibly hold proof sections to English
   reasoning pending eval (§2).
2. **review_language default:** ✅ default to detected paper language, resolved
   in the worker; explicit user pick overrides (§3.5).
3. **RTL:** ✅ descoped from v1 — LTR languages first (§3.9).
4. **Site UI i18n (PR-H):** ✅ lowest priority / deferred; when built, the
   site-language default comes from the **browser locale**
   (`navigator.language` / `Accept-Language`), not region/IP geolocation.
5. **Stranded code:** ✅ build fresh on `dev`; stranded PR-1 is reference-only
   (§3.4).
6. **Quality honesty:** ✅ surface a "best in English" note for non-English
   reviews; PR-F measures the real quality delta before we lean on it.

**Still open (not blocking PR-A):**
7. **Language scope:** which locales to support first? Bounds the name catalog
   (PR-B), label translations (PR-E), and eval set (PR-F). Decide at PR-B.
