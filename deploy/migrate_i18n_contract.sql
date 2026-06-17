-- Migration: multilingual contract fields on reviews.
--
-- Additive first step of the multilingual rollout (see docs/MULTILINGUAL_PLAN.md):
--   - no behavior change yet (columns stay NULL until the language PRs populate them)
--   - reuses the existing result_json column for structured output (no review_json)
--   - no locale-specific rendering yet
--
-- review_language NULL/empty means "follow the detected paper_language"
-- (resolved in the worker). Verbatim quotes always stay in the paper's source
-- language regardless of these fields.
--
-- DEPLOY ORDER: apply this to a Supabase project BEFORE deploying the web /
-- worker build that references these columns. The /api/review SELECT and the
-- submit/finalize writes name them, so a missing column fails every review
-- read / write (Postgres 42703). Apply to preview first, then prod.
--
-- Idempotent: safe to re-run in the SQL editor. (For a large reviews table you
-- may prefer `create index concurrently` — run those outside a transaction.)

alter table reviews add column if not exists site_language text;
alter table reviews add column if not exists review_language text;
alter table reviews add column if not exists paper_language text;
alter table reviews add column if not exists paper_language_source text;
alter table reviews add column if not exists text_direction text;

alter table reviews drop constraint if exists reviews_text_direction_check;
alter table reviews add constraint reviews_text_direction_check
  check (text_direction in ('ltr', 'rtl') or text_direction is null);

create index if not exists idx_reviews_review_language on reviews (review_language);
create index if not exists idx_reviews_paper_language on reviews (paper_language);
create index if not exists idx_reviews_site_language on reviews (site_language);
