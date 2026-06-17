# Multilingual Rollout Backlog

This document is the implementation backlog for making coarse support
multilingual site UX and multilingual review output without creating a
hard-to-merge long-lived rewrite branch.

It is intentionally separate from `docs/DEV_BACKLOG.md` because this work
touches hot files on `dev` and should ship as a stack of small PRs, each of
which can be preview-validated and merged independently.

## Goals

- Make `site_language` the primary user-facing locale control.
- Default `review_language` to `site_language`.
- Detect `paper_language` from the submitted paper, with override support.
- Keep `analysis_language` internal and system-controlled.
- Preserve review quality across languages by keeping canonical reasoning and
  localizing structured output rather than translating the entire prompt
  catalog up front.
- Minimize merge pain against a moving `origin/dev`.

## Non-goals

- Do not replace the entire review pipeline in one PR.
- Do not pretranslate every prompt into every language.
- Do not make translated prompts the system of record.
- Do not remove `result_markdown` until the JSON path has shipped and soaked.

## Merge Strategy

Use a PR stack on top of `dev`, not one implementation mega-branch.

Recommended branch names:

1. `codex/i18n-01-schema-contract`
2. `codex/i18n-02-site-locale`
3. `codex/i18n-03-review-json`
4. `codex/i18n-04-language-context`
5. `codex/i18n-05-structure-quote-hardening`
6. `codex/i18n-06-review-localization`
7. `codex/i18n-07-routing-evals`

Rules:

- Rebase each PR branch onto the latest `origin/dev` before opening the PR.
- Rebase again immediately before merge if `dev` moved.
- Keep each PR additive and backward-compatible.
- Prefer adding new helper modules over deeply rewriting hot files.
- Validate each deploy-affecting PR in preview before merging into `dev`.

## Shared Contract

Add a shared language contract and reuse it in Python and TypeScript.

Python target:

```python
class LanguageContext(BaseModel):
    site_language: str = "en"
    review_language: str = "en"
    paper_language: str = ""
    analysis_language: str = "en"
    text_direction: Literal["ltr", "rtl"] = "ltr"
    paper_language_source: Literal["detected", "user", "default"] = "default"
```

TypeScript target:

```ts
export type TextDirection = "ltr" | "rtl";

export interface LanguageContext {
  site_language: string;
  review_language: string;
  paper_language: string | null;
  analysis_language: string | null;
  text_direction: TextDirection;
  paper_language_source?: "detected" | "user" | "default";
}
```

Structured review target:

```ts
export interface StructuredReview {
  title: string;
  domain: string;
  taxonomy: string;
  date: string;
  language: LanguageContext;
  overall_feedback: {
    summary: string;
    assessment: string;
    recommendation: string;
    revision_targets: string[];
    issues: { title: string; body: string }[];
  };
  detailed_comments: {
    number: number;
    title: string;
    quote_original: string;
    quote_translation?: string | null;
    feedback: string;
    status: string;
    severity: "critical" | "major" | "minor";
    confidence: "high" | "medium" | "low";
  }[];
}
```

## PR 1: Schema And API Contract

Scope:

- Add nullable language fields to `reviews`.
- Add typed fields to web and Python models.
- Accept `site_language` from the submit path.
- Preserve all current behavior when fields are unset.

Files:

- `deploy/supabase_schema.sql`
- `web/src/lib/types.ts`
- `src/coarse/types.py`
- `web/src/app/api/submit/route.ts`
- `web/src/app/api/review/[id]/route.ts`
- `web/src/app/api/mcp-finalize/route.ts`
- `deploy/mcp_server.py`

Schema target:

```sql
alter table reviews add column if not exists site_language text;
alter table reviews add column if not exists review_language text;
alter table reviews add column if not exists paper_language text;
alter table reviews add column if not exists analysis_language text;
alter table reviews add column if not exists text_direction text
  check (text_direction in ('ltr', 'rtl'));
alter table reviews add column if not exists paper_language_source text;
alter table reviews add column if not exists review_json jsonb;
```

Acceptance:

- Existing submissions still work with no client changes.
- Existing reviews still load from `result_markdown`.
- No UI behavior change yet.

Preview checks:

- Submit a paper through preview web.
- Confirm new columns are written or left null safely.
- Confirm review status page still works for old and new rows.

## PR 2: Site Locale Layer

Scope:

- Add visible `site_language` control to the web app.
- Localize static UI strings only.
- Set `review_language = site_language` by default on submit.
- Add `dir="rtl"` support for supported locales.

Files:

- `web/src/app/page.tsx`
- `web/src/components/LanguagePicker.tsx`
- `web/src/lib/i18n.ts`
- `web/src/app/status/[id]/page.tsx`
- `web/src/components/ReviewDisplay.tsx`
- any shared layout/header components that contain static text

Implementation notes:

- Keep default locale `en`.
- Start with a small supported locale list.
- Do not change pipeline behavior yet.
- Keep locale helpers isolated in `web/src/lib/i18n.ts`.

Acceptance:

- Site labels switch languages.
- Review output remains unchanged.
- RTL layout is readable for Arabic or Hebrew.

Preview checks:

- Form labels and status text localize.
- Submission still succeeds across locale changes.

## PR 3: Structured Review JSON

Scope:

- Add canonical JSON serialization for reviews.
- Persist `review_json` next to `result_markdown`.
- Read `review_json` in the web UI when present.
- Keep markdown parsing as fallback for old reviews.

Files:

- `src/coarse/synthesis.py`
- `web/src/lib/parseReview.ts`
- `web/src/components/ReviewDisplay.tsx`
- `web/src/app/api/review/[id]/route.ts`
- `deploy/mcp_server.py`
- any finalize route writing review data

Implementation notes:

- Add `serialize_review(review, language_context) -> dict`.
- Do not remove `render_review(review)`.
- Prefer a new reader path over mutating the old markdown parser heavily.

Acceptance:

- New reviews render from JSON.
- Old reviews still render from markdown.
- No functional regression in the review page.

Preview checks:

- Verify new rows store both JSON and markdown.
- Compare rendering of the same review through both paths.

## PR 4: Pipeline Language Context

Scope:

- Create and propagate `LanguageContext`.
- Detect `paper_language` after extraction.
- Default `review_language` from `site_language`.
- Keep `analysis_language = "en"` initially.

Files:

- `src/coarse/pipeline.py`
- `src/coarse/language.py`
- `src/coarse/types.py`
- `web/src/app/api/submit/route.ts`
- `web/src/lib/mcpHandoff.ts`
- `deploy/mcp_server.py`
- `deploy/modal_worker.py`
- any headless review or finalize code paths

Implementation notes:

- The first pass can use a cheap language detector plus user override.
- Keep the detector isolated in `src/coarse/language.py`.
- Make no claim yet that review text will match `review_language`.

Acceptance:

- Web, CLI, and MCP all preserve the same language metadata.
- Paper language is detected and stored for new reviews.

Preview checks:

- Submit papers in English and one non-English language.
- Confirm the detected language survives to the finalized row.

## PR 5: Structure And Quote Hardening

Scope:

- Remove the strongest English-only failure points from paper parsing and
  quote verification.
- Keep current English heuristics as fallback.

Files:

- `src/coarse/structure.py`
- `src/coarse/quote_verify.py`
- `src/coarse/extraction.py`
- `web/src/lib/estimateCost.ts`
- related tests

Implementation notes:

- Add multilingual section typing that maps to canonical `SectionType`.
- Do not rely primarily on English headings like `abstract`, `theorem`, or
  `proof`.
- Replace whitespace-token prefiltering with Unicode-aware segmentation or
  normalized character n-grams.
- Make token estimates less English-specific.

Acceptance:

- English behavior stays stable.
- At least one CJK paper and one Romance-language paper pass smoke tests.

Preview checks:

- Run representative papers through preview and inspect section typing and
  quote survival.

## PR 6: Review Localization

Scope:

- Localize the final human-facing review into `review_language`.
- Keep canonical prompts and schemas in English.
- Preserve source-language quotes for verification.

Files:

- `src/coarse/prompts.py`
- `src/coarse/localization.py`
- `src/coarse/synthesis.py`
- `src/coarse/pipeline.py`
- review rendering and finalize code paths

Implementation notes:

- Add one central language-aware prompt suffix rather than editing every prompt
  independently.
- Localize only human-facing fields:
  - overview summary
  - assessment
  - recommendation
  - issue titles and bodies
  - comment titles
  - feedback
  - optional quote gloss
- Keep `quote_original` unchanged.

Acceptance:

- The same structured review can render to more than one locale.
- Quote verification still uses source-language text only.

Preview checks:

- Generate the same paper review in at least two review languages and compare
  structure parity.

## PR 7: Routing Evals

Scope:

- Decide whether `analysis_language` should remain English-pivot or vary by
  language and model.

Files:

- `tests/`
- `scripts/`
- any eval harness modules under `src/coarse/`

Implementation notes:

- Compare:
  - direct target-language analysis
  - English-pivot analysis plus localized output
  - adaptive router
- Measure:
  - issue recall
  - false-positive rate
  - quote fidelity
  - expert preference
  - translation adequacy

Acceptance:

- `analysis_language` policy is backed by evals rather than assumption.

## Hot Files To Touch Carefully

These files are likely to keep moving on `dev`, so keep edits narrow:

- `web/src/app/page.tsx`
- `web/src/app/api/submit/route.ts`
- `deploy/supabase_schema.sql`
- `src/coarse/pipeline.py`
- `src/coarse/synthesis.py`
- `deploy/mcp_server.py`

Conflict minimization rules:

- Prefer thin adapters in hot files.
- Put new logic in new modules.
- Do not move large blocks unless necessary.
- Do not delete old interfaces until the replacement has soaked in preview.

## Preview-First Rollout

Every PR in this backlog touches web, schema, worker, or pipeline behavior.
That means the repo's preview rules apply:

1. Merge feature branches into `dev`, not `main`.
2. Let preview Vercel and preview Modal deploy from `dev`.
3. Validate against preview Supabase, not production.
4. Merge `dev` to `main` only after preview passes.

## Suggested Order Of Execution

1. PR 1: schema and API contract
2. PR 2: site locale layer
3. PR 3: structured review JSON
4. PR 4: pipeline language context
5. PR 5: structure and quote hardening
6. PR 6: review localization
7. PR 7: routing evals

This order keeps the rollout additive, preview-testable, and straightforward
to rebase as `dev` continues to move.
