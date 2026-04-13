-- Migration: count only actually-submitted active reviews for capacity checks.
--
-- `/api/presign` inserts a queued review row before the user uploads a file or
-- submits contact details. Capacity checks must exclude these abandoned presign
-- rows, otherwise they can lock out legitimate submissions. A review is
-- considered "submitted" once `/api/submit` has inserted `review_emails`.

create index if not exists idx_reviews_status_created_at
  on reviews (status, created_at);

create or replace function count_active_submitted_reviews(since timestamptz)
returns bigint
language sql
security definer
as $$
  select count(*)
  from reviews r
  where r.created_at >= since
    and r.status in ('queued', 'running', 'extracting', 'extracted')
    and exists (
      select 1
      from review_emails e
      where e.review_id = r.id
    );
$$;
