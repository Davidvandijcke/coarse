-- Phase 2: Drop the email column from reviews after verifying phase 1 code works.
-- Only run this AFTER the phase 1 migration + code deploy is verified in production.

ALTER TABLE reviews DROP COLUMN email;
