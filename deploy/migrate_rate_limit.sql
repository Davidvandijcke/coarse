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

create or replace function public.check_rate_limit(
  p_ip text,
  p_endpoint text,
  p_window_seconds int,
  p_max_requests int
) returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  request_count int;
  window_start timestamptz;
begin
  if p_ip is null or char_length(p_ip) < 1 or char_length(p_ip) > 128 then
    raise exception 'invalid rate-limit IP'
      using errcode = '22023';
  end if;
  if p_endpoint is null or char_length(p_endpoint) > 64 or p_endpoint not in (
    'presign',
    'submit',
    'cancel',
    'delete',
    'cli-handoff',
    'mcp-finalize'
  ) then
    raise exception 'invalid rate-limit endpoint'
      using errcode = '22023';
  end if;
  if p_window_seconds is null or p_window_seconds < 1 or p_window_seconds > 3600
     or p_max_requests is null or p_max_requests < 1 or p_max_requests > 1000 then
    raise exception 'invalid rate-limit bounds'
      using errcode = '22023';
  end if;

  window_start := pg_catalog.now() - pg_catalog.make_interval(secs => p_window_seconds);

  -- Serialize concurrent calls for the same (ip, endpoint) pair
  perform pg_catalog.pg_advisory_xact_lock(
    pg_catalog.hashtext(p_ip),
    pg_catalog.hashtext(p_endpoint)
  );

  select count(*) into request_count
  from public.rate_limit_log as log
  where log.ip = p_ip
    and log.endpoint = p_endpoint
    and log.created_at > window_start;

  if request_count >= p_max_requests then
    return false;
  end if;

  insert into public.rate_limit_log (ip, endpoint) values (p_ip, p_endpoint);

  delete from public.rate_limit_log as log
  where log.ip = p_ip
    and log.endpoint = p_endpoint
    and log.created_at < window_start;

  -- Global cleanup: ~1% of calls, purge all entries older than 1 hour
  if pg_catalog.random() < 0.01 then
    delete from public.rate_limit_log
    where created_at < pg_catalog.now() - interval '1 hour';
  end if;

  return true;
end;
$$;

revoke execute on function public.check_rate_limit(text, text, integer, integer)
  from public, anon, authenticated;
grant execute on function public.check_rate_limit(text, text, integer, integer)
  to service_role;

alter table rate_limit_log enable row level security;
