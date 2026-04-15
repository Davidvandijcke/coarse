-- Restore mcp_handoff_tokens after the erroneous drop in commit 8fd3720.
--
-- The prior migration (migrate_drop_mcp_handoff_tokens.sql, since deleted)
-- removed the table despite four live v1.3.0 call sites still depending on
-- it:
--   - web/src/app/api/cli-handoff/route.ts    (INSERT, cleanup RPC)
--   - web/src/app/h/[token]/route.ts           (SELECT)
--   - web/src/app/api/mcp-finalize/route.ts    (SELECT + UPDATE)
--
-- The release-pre-pr review caught this before the v1.3.0 merge to main. This
-- migration recreates the table + index + cleanup function idempotently so a
-- DB that had the drop applied (preview) gets the table back on the next
-- `scripts/apply_migrations.sh` run. Fresh bootstraps from
-- `deploy/supabase_schema.sql` already get the table and this migration is a
-- no-op for them.

create table if not exists mcp_handoff_tokens (
  token uuid primary key default gen_random_uuid(),
  paper_id uuid not null references reviews(id) on delete cascade,
  created_at timestamptz default now(),
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create index if not exists idx_mcp_handoff_expiry
  on mcp_handoff_tokens (expires_at);

alter table mcp_handoff_tokens enable row level security;

create or replace function cleanup_mcp_handoff_tokens()
returns int
language plpgsql
security definer
as $$
declare
  deleted_count int;
begin
  delete from mcp_handoff_tokens
  where expires_at < now()
     or (consumed_at is not null and consumed_at < now() - interval '5 minutes');
  get diagnostics deleted_count = row_count;
  return deleted_count;
end;
$$;
