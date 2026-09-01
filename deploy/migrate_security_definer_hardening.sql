-- Harden every privileged RPC that is reachable through the exposed public schema.
-- Existing migrations created these functions before explicit function grants and
-- fixed search paths were part of the repository's security baseline.
--
-- PostgreSQL grants EXECUTE on new functions to PUBLIC by default. RLS on the
-- underlying tables is not a substitute: SECURITY DEFINER runs with the owner's
-- privileges. Recreate the functions with schema-qualified relations, then make
-- service_role the only Data API role that can execute them.

begin;

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

create or replace function public.count_reviews_since(since timestamptz)
returns bigint
language sql
security definer
set search_path = ''
as $$
  select count(*) from public.reviews where created_at >= since;
$$;

revoke execute on function public.count_reviews_since(timestamptz)
  from public, anon, authenticated;
grant execute on function public.count_reviews_since(timestamptz)
  to service_role;

create or replace function public.count_active_submitted_reviews(since timestamptz)
returns bigint
language sql
security definer
set search_path = ''
as $$
  select count(*)
  from public.reviews r
  where r.created_at >= since
    and r.status in ('queued', 'running', 'extracting', 'extracted')
    and exists (
      select 1
      from public.review_emails e
      where e.review_id = r.id
    );
$$;

revoke execute on function public.count_active_submitted_reviews(timestamptz)
  from public, anon, authenticated;
grant execute on function public.count_active_submitted_reviews(timestamptz)
  to service_role;

create or replace function public.cleanup_handoff_tokens()
returns int
language plpgsql
security definer
set search_path = ''
as $$
declare
  deleted_count int;
begin
  delete from public.handoff_tokens
  where expires_at < pg_catalog.now()
     or (
       consumed_at is not null
       and consumed_at < pg_catalog.now() - interval '5 minutes'
     );
  get diagnostics deleted_count = row_count;
  return deleted_count;
end;
$$;

revoke execute on function public.cleanup_handoff_tokens()
  from public, anon, authenticated;
grant execute on function public.cleanup_handoff_tokens()
  to service_role;

notify pgrst, 'reload schema';

commit;
