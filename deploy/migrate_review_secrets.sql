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

create table if not exists review_secrets (
  review_id uuid primary key references reviews(id) on delete cascade,
  user_api_key text not null,
  created_at timestamptz default now()
);

alter table review_secrets enable row level security;

-- Intentionally no RLS policies: deny-all for anon and authenticated.
-- service_role bypasses RLS.

-- Index for the TTL cleanup cron (deletes rows older than N hours).
create index if not exists idx_review_secrets_created_at on review_secrets (created_at);
