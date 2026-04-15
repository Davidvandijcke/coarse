-- Retire the mcp_handoff_tokens table. The MCP server path was removed in
-- d0706b2 ("feat(release): retire MCP server path entirely (v1.3.0)") and
-- no runtime code references this table anymore. The superseded
-- deploy/migrate_mcp_handoff.sql was deleted alongside this migration; the
-- still-load-bearing parts of that migration (review_handoff_secrets,
-- reviews.taxonomy, widened reviews_status_check including 'extracting' and
-- 'extracted') are now inlined in deploy/supabase_schema.sql so fresh
-- projects bootstrap correctly without needing the old migration.
--
-- Idempotent: uses `drop ... if exists` so it's safe to run against:
-- - preview/prod DBs where the table still lingers from the earlier migration
-- - fresh DBs bootstrapped from the updated baseline that never had the table

drop table if exists mcp_handoff_tokens;
