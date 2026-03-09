-- Supabase schema for coarse (no-auth version)
-- Run this in the Supabase SQL editor to set up the database.

-- ============================================================================
-- Reviews
-- ============================================================================

create table reviews (
  id uuid primary key default gen_random_uuid(),   -- serves as the unique access key
  email text not null,
  paper_filename text not null,
  status text not null default 'queued'
    check (status in ('queued', 'running', 'done', 'failed')),
  paper_title text,
  domain text,
  result_markdown text,
  cost_usd numeric(8,4),
  duration_seconds int,
  error_message text,
  created_at timestamptz default now(),
  completed_at timestamptz
);

-- RLS: reads are open (UUID is unguessable, serves as access token).
-- All writes are done server-side via the service key, which bypasses RLS.
alter table reviews enable row level security;

create policy "Anyone can view reviews by id"
  on reviews for select using (true);

-- ============================================================================
-- Storage buckets
-- ============================================================================

-- Papers bucket: private. PDFs uploaded and deleted server-side via service key.
insert into storage.buckets (id, name, public) values ('papers', 'papers', false);

-- ============================================================================
-- Realtime: enable for review status updates
-- ============================================================================

alter publication supabase_realtime add table reviews;
