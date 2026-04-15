-- Migration: rename mcp_handoff_tokens -> handoff_tokens (and cleanup fn).
--
-- Context. The table stores single-use finalize tokens for the CLI /
-- subscription handoff flow (3 h TTL, one row per paper). Its `mcp_`
-- prefix is a historical accident from when the same table briefly
-- served the now-retired MCP server path. v1.3.0 retired MCP itself
-- (commit d0706b2) but deliberately kept this table because the CLI
-- handoff flow still depends on it end-to-end: `/api/cli-handoff` mints
-- the row, `/h/<token>` reads it, `/api/mcp-finalize` validates and
-- consumes it.
--
-- PR #133 (commit 8fd3720) then misread the table's name as retired MCP
-- scaffolding, deleted `migrate_mcp_handoff.sql`, and added
-- `migrate_drop_mcp_handoff_tokens.sql` containing `drop table if
-- exists mcp_handoff_tokens`. The new supabase-migrate-preview workflow
-- ran that against the preview Supabase project, which broke the
-- subscription handoff on preview: every `POST /api/cli-handoff` now
-- returns `Failed to mint finalize token: Could not find the table
-- 'public.mcp_handoff_tokens' in the schema cache`. Production has not
-- been migrated yet (no prod-migrate workflow is wired up as of
-- 2026-04-15) and still holds the legacy table.
--
-- This migration repairs both states in one file so it runs correctly
-- against any project:
--
--   1. Preview Supabase (legacy table dropped by the bad migration):
--      step 1's rename is a no-op (legacy doesn't exist), step 2's
--      `create table if not exists handoff_tokens` creates the table
--      fresh with the correct shape. In-flight finalize tokens were
--      already lost when the drop ran — nothing to preserve here.
--
--   2. Production Supabase (legacy table still exists, never dropped):
--      step 1 renames `mcp_handoff_tokens` -> `handoff_tokens` in place,
--      preserving every row and the FK to reviews.id. Step 2's create
--      is a no-op because the table already exists under the new name.
--
--   3. Any fresh project bootstrapped after this migration lands:
--      step 1 is a no-op (no legacy), step 2 creates the table fresh.
--
-- Idempotent end-to-end: every DDL is guarded by `if [not] exists` or a
-- `do $$` existence check, so apply_migrations.sh can safely retry a
-- half-applied run.
--
-- The sibling `migrate_drop_mcp_handoff_tokens.sql` is deleted in the
-- same commit; the supabase-migrate-preview runner glob will no longer
-- pick it up. Projects that already applied it (preview) keep the row
-- in `schema_migrations`, which is harmless.

-- Step 1: rename legacy table and index in place when present.
do $$
begin
  if exists (
    select 1 from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public'
      and c.relname = 'mcp_handoff_tokens'
      and c.relkind = 'r'
  ) and not exists (
    select 1 from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public'
      and c.relname = 'handoff_tokens'
      and c.relkind = 'r'
  ) then
    execute 'alter table public.mcp_handoff_tokens rename to handoff_tokens';
  end if;

  if exists (
    select 1 from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public'
      and c.relname = 'idx_mcp_handoff_expiry'
      and c.relkind = 'i'
  ) then
    execute 'alter index public.idx_mcp_handoff_expiry rename to idx_handoff_expiry';
  end if;
end $$;

-- Step 2: create fresh on any DB that doesn't have the table under the
-- new name (preview after the bad drop, or a fully fresh bootstrap).
-- Shape mirrors the original mcp_handoff_tokens definition exactly so
-- the foreign key, cascade behavior, and primary-key type are unchanged.
create table if not exists handoff_tokens (
  token uuid primary key default gen_random_uuid(),
  paper_id uuid not null references reviews(id) on delete cascade,
  created_at timestamptz default now(),
  expires_at timestamptz not null,
  consumed_at timestamptz
);

create index if not exists idx_handoff_expiry
  on handoff_tokens (expires_at);

alter table handoff_tokens enable row level security;

-- Step 3: install the renamed cleanup function. Same body as the
-- original cleanup_mcp_handoff_tokens — expiry-or-consumed sweep with
-- a 5-minute grace window for retryable finalize callbacks.
create or replace function cleanup_handoff_tokens()
returns int
language plpgsql
security definer
as $$
declare
  deleted_count int;
begin
  delete from handoff_tokens
  where expires_at < now()
     or (consumed_at is not null and consumed_at < now() - interval '5 minutes');
  get diagnostics deleted_count = row_count;
  return deleted_count;
end;
$$;

drop function if exists cleanup_mcp_handoff_tokens();

-- Step 4: nudge PostgREST to reload its schema cache so the renamed
-- table and function are visible to the Supabase REST/RPC client
-- immediately instead of waiting for the periodic refresh.
notify pgrst, 'reload schema';
