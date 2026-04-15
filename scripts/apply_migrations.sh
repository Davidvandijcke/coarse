#!/usr/bin/env bash
set -euo pipefail

# Apply each deploy/migrate_*.sql once, tracked in a schema_migrations table.
#
# Usage:
#   DATABASE_URL=postgresql://... scripts/apply_migrations.sh
#   scripts/apply_migrations.sh --dry-run
#
# Does NOT run deploy/supabase_schema.sql — that file is the one-shot baseline
# and contains non-idempotent CREATE TABLE statements. Run it manually via the
# Supabase SQL editor when bootstrapping a fresh project; migrations only
# extend from there.

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=1
  shift
fi

: "${DATABASE_URL:?DATABASE_URL must be set}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MIGRATIONS_DIR="$REPO_ROOT/deploy"

psql_exec() { psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -Atq "$@"; }

psql_exec -c "
create table if not exists schema_migrations (
  name text primary key,
  applied_at timestamptz not null default now()
);
"

APPLIED="$(psql_exec -c 'select name from schema_migrations')"

status=0
for f in "$MIGRATIONS_DIR"/migrate_*.sql; do
  name="$(basename "$f" .sql)"
  if echo "$APPLIED" | grep -qx "$name"; then
    echo "skip   $name (already applied)"
    continue
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "would  $name"
    continue
  fi
  echo "apply  $name"
  if psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"; then
    psql_exec -c "insert into schema_migrations (name) values ('$name')"
  else
    echo "::error::migration $name failed"
    status=1
    break
  fi
done

exit "$status"
