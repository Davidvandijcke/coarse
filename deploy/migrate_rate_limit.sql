-- Migration: add rate limiting (rate_limit_log table + check_rate_limit RPC)
-- Run this in the Supabase SQL editor on existing deployments.

create table if not exists rate_limit_log (
  id bigint generated always as identity primary key,
  ip text not null,
  endpoint text not null,
  created_at timestamptz default now()
);

create index if not exists idx_rate_limit_lookup on rate_limit_log (ip, endpoint, created_at);

-- Drop existing version (signature may have had default params)
drop function if exists check_rate_limit(text, text, integer, integer);

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

  select count(*) into request_count
  from rate_limit_log
  where ip = p_ip
    and endpoint = p_endpoint
    and created_at > window_start;

  if request_count >= p_max_requests then
    return false;
  end if;

  insert into rate_limit_log (ip, endpoint) values (p_ip, p_endpoint);

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

alter table rate_limit_log enable row level security;
