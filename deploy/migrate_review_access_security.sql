-- Migration: close public reads on reviews, add the cancelled status, and
-- preserve read-only access for pre-hardening legacy review links.
--
-- Previous schema versions exposed every review row to the anon key because
-- the select policy was `using (true)`. The web frontend now reads reviews
-- through authenticated server routes instead, so public SELECT access is no
-- longer needed.

drop policy if exists "Anyone can view reviews by id" on reviews;

alter table reviews
  add column if not exists access_token_required boolean;

update reviews
set access_token_required = false
where access_token_required is null;

alter table reviews
  alter column access_token_required set default false;

alter table reviews
  alter column access_token_required set not null;

alter table reviews
  drop constraint if exists reviews_status_check;

alter table reviews
  add constraint reviews_status_check
  check (status in (
    'queued',
    'running',
    'extracting',
    'extracted',
    'done',
    'failed',
    'cancelled'
  ));
