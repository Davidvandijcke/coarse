-- Phase 1: Move email from reviews to a separate service_role-only table.
-- Run this in the Supabase SQL editor BEFORE deploying the corresponding code changes.
--
-- After running this, deploy the code, verify everything works, then run phase 2.

BEGIN;

-- Create separate email table with strict RLS (no anon policy = deny all)
CREATE TABLE review_emails (
  review_id uuid PRIMARY KEY REFERENCES reviews(id) ON DELETE CASCADE,
  email text NOT NULL,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE review_emails ENABLE ROW LEVEL SECURITY;

-- Backfill existing emails
INSERT INTO review_emails (review_id, email)
SELECT id, email FROM reviews WHERE email IS NOT NULL;

-- Make email nullable so new code can stop writing it
ALTER TABLE reviews ALTER COLUMN email DROP NOT NULL;

COMMIT;
