-- Migration: close public reads on reviews and add the cancelled status.
--
-- Previous schema versions exposed every review row to the anon key because
-- the select policy was `using (true)`. The web frontend now reads reviews
-- through authenticated server routes instead, so public SELECT access is no
-- longer needed.

drop policy if exists "Anyone can view reviews by id" on reviews;

alter table reviews
  drop constraint if exists reviews_status_check;

alter table reviews
  add constraint reviews_status_check
  check (status in ('queued', 'running', 'done', 'failed', 'cancelled'));
