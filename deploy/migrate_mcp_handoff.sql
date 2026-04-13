-- Migration: mcp_handoff_tokens — capability tokens for the web→MCP round-trip.
--
-- Rationale: deploy/mcp_server.py deliberately does NOT hold a Supabase
-- service key. For each review handed off from the web form to a user's
-- chat host (Claude.ai, ChatGPT, Claude Code, Gemini CLI), the Next.js
-- backend mints:
--
--   1. A single-use finalize token (row in this table, 3-hour TTL —
--      see FINALIZE_TOKEN_TTL_MINUTES in web/src/app/api/mcp-handoff/
--      route.ts and web/src/app/api/cli-handoff/route.ts).
--   2. A 3-hour signed download URL for the stored PDF, re-signed fresh
--      on every fetch of /h/<token> — see PDF_SIGNED_URL_TTL_SECONDS in
--      web/src/app/h/[token]/route.ts. The URL rolls forward on each
--      access as long as the finalize token is still valid, so long-
--      running agent sessions don't race a short download TTL.
--
-- Both capabilities travel in the clipboard prompt the user pastes into
-- their chat host. The MCP server uses the signed URL to fetch the PDF
-- and, at finalize_review time, POSTs the rendered markdown back to
-- /api/mcp-finalize with the token. /api/mcp-finalize validates the
-- token, upserts the reviews row, and consumes the token so it can't
-- be reused.
--
-- Threat model: if the clipboard prompt leaks to a third party, the
-- attacker can (a) download the paper for the next 3 hours and
-- (b) write a review into exactly one reviews row for the next 3
-- hours. No cross-user data, no schema-wide writes, no secrets.
-- The MCP server holds zero persistent credentials.
--
-- TTL source of truth: the actual durations live in TypeScript constants
-- in the route files above, not in this migration. Update those to
-- change the lifetimes; this SQL just defines the storage.
--
-- Run this in the Supabase SQL editor after pulling this branch.

create table if not exists mcp_handoff_tokens (
  token uuid primary key default gen_random_uuid(),
  paper_id uuid not null references reviews(id) on delete cascade,
  created_at timestamptz default now(),
  expires_at timestamptz not null,
  consumed_at timestamptz
);

-- Expiry sweeps are the only read path we care about besides point lookups
-- by token, so a single index on expires_at is enough.
create index if not exists idx_mcp_handoff_expiry
  on mcp_handoff_tokens (expires_at);

-- RLS: deny all anonymous access; only the service role (used by
-- /api/mcp-handoff and /api/mcp-finalize on the Next.js backend)
-- can read or write. This mirrors review_emails + rate_limit_log.
alter table mcp_handoff_tokens enable row level security;

-- Cleanup helper — safe to run from a cron or inside /api/mcp-handoff
-- as an opportunistic sweep. Removes any token that's expired OR that
-- was consumed more than 5 minutes ago (keeping consumed tokens briefly
-- so the client-side flow can idempotently retry if a network blip
-- hides the success response).
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

-- Browser proof-of-possession for follow-up routes after /api/presign.
-- The public review UUID remains readable, but callers must also present
-- this high-entropy secret to /api/submit, /api/cli-handoff, /api/mcp-extract,
-- and /api/mcp-handoff. Store only the SHA-256 hash server-side.
create table if not exists review_handoff_secrets (
  review_id uuid primary key references reviews(id) on delete cascade,
  secret_hash text not null check (length(secret_hash) = 64),
  created_at timestamptz default now()
);

alter table review_handoff_secrets enable row level security;

create index if not exists idx_review_handoff_secrets_created_at
  on review_handoff_secrets (created_at);

-- ============================================================================
-- Expand reviews.status enum to cover the MCP extract-and-handoff flow.
-- ============================================================================
--
-- The existing check constraint only allows ('queued','running','done','failed').
-- The subscription-routed flow needs two new terminal-adjacent states:
--
--   extracting → Modal do_extract is currently running (post-upload,
--                pre-handoff). Browser shows a spinner on the "Review
--                with my subscription" button while this is active.
--   extracted  → Modal do_extract finished, state blob written to
--                papers/<uuid>.mcp.json. /api/mcp-handoff will now
--                mint a signed URL for that blob + a finalize token,
--                and the handoff prompt is ready to copy.
--
-- Idempotent: drop-if-exists + re-create covers re-running the full
-- migration on an already-migrated DB.

alter table reviews drop constraint if exists reviews_status_check;
alter table reviews add constraint reviews_status_check
  check (status in (
    'queued',
    'running',
    'extracting',
    'extracted',
    'done',
    'failed'
  ));

alter table reviews add column if not exists taxonomy text;
