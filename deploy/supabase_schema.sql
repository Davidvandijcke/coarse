-- Supabase schema for coarse (no-auth version)
-- Run this in the Supabase SQL editor to set up the database.

-- ============================================================================
-- Reviews
-- ============================================================================

create table reviews (
  id uuid primary key default gen_random_uuid(),   -- serves as the unique access key
  paper_filename text not null,
  status text not null default 'queued'
    check (status in ('queued', 'running', 'done', 'failed')),
  paper_title text,
  model text,
  domain text,
  result_markdown text,
  paper_markdown text,
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
-- Review emails (PII separated from public review data)
-- ============================================================================

create table review_emails (
  review_id uuid primary key references reviews(id) on delete cascade,
  email text not null,
  created_at timestamptz default now()
);

-- RLS: no anon policy = deny all. Only service_role (which bypasses RLS) can read/write.
alter table review_emails enable row level security;

-- ============================================================================
-- Storage buckets
-- ============================================================================

-- Papers bucket: private. PDFs uploaded and deleted server-side via service key.
insert into storage.buckets (id, name, public) values ('papers', 'papers', false);

-- ============================================================================
-- Rate limiting
-- ============================================================================

create table rate_limit_log (
  id bigint generated always as identity primary key,
  ip text not null,
  endpoint text not null,
  created_at timestamptz default now()
);

create index idx_rate_limit_lookup on rate_limit_log (ip, endpoint, created_at);

-- Returns true if the request is allowed, false if rate-limited.
-- Called via supabase.rpc("check_rate_limit", { p_ip, p_endpoint, p_window_seconds, p_max_requests }).
create or replace function check_rate_limit(
  p_ip text,
  p_endpoint text,
  p_window_seconds int,
  p_max_requests int
) returns boolean
language plpgsql
security definer
as $$
declare
  request_count int;
  window_start timestamptz := now() - (p_window_seconds || ' seconds')::interval;
begin
  -- Serialize concurrent calls for the same (ip, endpoint) pair
  perform pg_advisory_xact_lock(hashtext(p_ip), hashtext(p_endpoint));

  -- Count recent requests in window
  select count(*) into request_count
  from rate_limit_log
  where ip = p_ip
    and endpoint = p_endpoint
    and created_at > window_start;

  -- Over limit → deny
  if request_count >= p_max_requests then
    return false;
  end if;

  -- Log this request
  insert into rate_limit_log (ip, endpoint) values (p_ip, p_endpoint);

  -- Opportunistic cleanup: purge expired entries for this ip/endpoint
  delete from rate_limit_log
  where ip = p_ip
    and endpoint = p_endpoint
    and created_at < window_start;

  -- Global cleanup: ~1% of calls, purge all entries older than 1 hour
  if random() < 0.01 then
    delete from rate_limit_log where created_at < now() - interval '1 hour';
  end if;

  return true;
end;
$$;

-- RLS: deny all anonymous access. Only service_role (which bypasses RLS) calls this.
alter table rate_limit_log enable row level security;

-- ============================================================================
-- Realtime: enable for review status updates
-- ============================================================================

alter publication supabase_realtime add table reviews;

-- ============================================================================
-- System status (capacity management)
-- ============================================================================

-- Singleton row: manual kill switch + banner message for the web frontend.
-- Flip from the Supabase SQL editor:
--   UPDATE system_status SET accepting_reviews = false,
--     banner_message = 'High traffic — use the CLI: pip install coarse',
--     updated_at = now() WHERE id = 1;
create table system_status (
  id int primary key default 1 check (id = 1),
  accepting_reviews boolean not null default true,
  banner_message text,
  updated_at timestamptz default now()
);

insert into system_status (id) values (1);

alter table system_status enable row level security;

create policy "Anyone can read system status"
  on system_status for select using (true);

alter publication supabase_realtime add table system_status;

-- Helper for monitoring cron: count reviews since a given timestamp.
create or replace function count_reviews_since(since timestamptz)
returns bigint language sql security definer as $$
  select count(*) from reviews where created_at >= since;
$$;
