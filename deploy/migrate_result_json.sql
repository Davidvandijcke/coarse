-- Migration: persist the structured Review JSON alongside the rendered markdown.
--
-- The pipeline already builds a structured `Review` (Pydantic) with stable
-- per-comment numbers, severity, and confidence, but only the rendered markdown
-- (result_markdown) was stored. This adds result_json (jsonb) so downstream
-- features — the per-comment "Discuss" chat, and a future second-round review —
-- can work from the authoritative structure instead of re-parsing markdown.
--
-- Backfill is intentionally omitted: existing reviews keep result_json NULL and
-- consumers fall back to the markdown parse. The Modal worker writes it for new
-- web reviews; the CLI-handoff finalize path leaves it NULL until that path is
-- updated.
--
-- Idempotent: safe to re-run in the SQL editor.

alter table reviews add column if not exists result_json jsonb;
