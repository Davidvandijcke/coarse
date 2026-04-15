-- One-shot bootstrap for the schema_migrations tracking table used by
-- scripts/apply_migrations.sh (and the supabase-migrate-preview.yml workflow).
--
-- Run this ONCE per Supabase project (preview AND prod), via the Supabase SQL
-- editor, BEFORE the first run of scripts/apply_migrations.sh. It creates the
-- tracking table and backfills it with every migration that was already
-- applied by hand during initial setup, so apply_migrations.sh will skip
-- re-applying destructive historical migrations like migrate_email_phase2.
--
-- The seed list deliberately does NOT include migrate_drop_mcp_handoff_tokens
-- — that one is a post-bootstrap migration that should run against any DB
-- that still has the retired mcp_handoff_tokens table lingering from the
-- earlier migrate_mcp_handoff.sql. It is idempotent (`drop table if exists`)
-- so it is a no-op on a fresh project bootstrapped from the current baseline.
--
-- Idempotent — safe to re-run. Only adds names that are missing.

create table if not exists schema_migrations (
  name text primary key,
  applied_at timestamptz not null default now()
);

insert into schema_migrations (name) values
  ('migrate_active_review_capacity'),
  ('migrate_email_phase1'),
  ('migrate_email_phase2'),
  ('migrate_rate_limit'),
  ('migrate_review_access_security'),
  ('migrate_review_secrets')
on conflict (name) do nothing;
