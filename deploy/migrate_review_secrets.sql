-- Migration: add review_secrets side-table to ferry user OpenRouter keys
-- without embedding them in Modal's spawn() payload.
--
-- Before this migration, the frontend included `user_api_key` in the JSON body
-- of the Modal webhook request. `run_review` then called `do_review.spawn(req.model_dump())`,
-- which serialized the dict (including the key) into Modal's managed queue until the
-- worker consumed it. That's the queue-persistence leak vector task 3(a) addresses.
--
-- After this migration, the frontend writes the key to `review_secrets` with a
-- service-role client (bypassing RLS). The Modal worker reads + deletes the row
-- in one shot via _fetch_and_consume_user_key(). A GitHub Actions cron sweeps any
-- rows older than 3 hours as a safety net (Modal's review timeout is 2h).
--
-- RLS model mirrors review_emails: enable RLS with NO policies, so anon and
-- authenticated callers hit deny-all. service_role bypasses RLS by design, so
-- the frontend (which uses SUPABASE_SERVICE_KEY) and the worker (same) can still
-- read and write.
--
-- Idempotent: safe to re-run in the SQL editor.
--
-- Rollout order: migration (this file) → Modal worker → Vercel. The backward-
-- compat `req.user_api_key` branch in the worker's _resolve_user_api_key lets
-- the Vercel deploy safely lag the Modal deploy. However, ROLLING BACK the
-- Modal worker AFTER Vercel has deployed is unsafe: the rolled-back worker
-- reads req.user_api_key from the webhook body, which the new Vercel no
-- longer sends, so every review 401s. If you need to roll back Modal, roll
-- back Vercel first (or temporarily re-enable `user_api_key` in the submit
-- route's Modal fetch body).

create table if not exists review_secrets (
  review_id uuid primary key references reviews(id) on delete cascade,
  user_api_key text not null check (length(user_api_key) > 0),
  created_at timestamptz default now()
);

alter table review_secrets enable row level security;

-- Intentionally no RLS policies: deny-all for anon and authenticated.
-- service_role bypasses RLS.

-- Index for the TTL cleanup cron (deletes rows older than N hours).
create index if not exists idx_review_secrets_created_at on review_secrets (created_at);
