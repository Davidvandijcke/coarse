"""Regression guards for privileged Supabase functions and migration order."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_DIR = REPO_ROOT / "deploy"

FUNCTION_DEFINITION_FILES = (
    "supabase_schema.sql",
    "migrate_rate_limit.sql",
    "migrate_active_review_capacity.sql",
    "migrate_rename_handoff_tokens.sql",
    "migrate_security_definer_hardening.sql",
)

PRIVILEGED_SIGNATURES = (
    "public.check_rate_limit(text, text, integer, integer)",
    "public.count_reviews_since(timestamptz)",
    "public.count_active_submitted_reviews(timestamptz)",
    "public.cleanup_handoff_tokens()",
)


def _sql_code(filename: str) -> str:
    source = (DEPLOY_DIR / filename).read_text(encoding="utf-8")
    return "\n".join(line.split("--", 1)[0] for line in source.splitlines())


def _normalized(filename: str) -> str:
    return re.sub(r"\s+", " ", _sql_code(filename)).strip().lower()


def test_every_security_definer_has_an_empty_search_path() -> None:
    for filename in FUNCTION_DEFINITION_FILES:
        source = _sql_code(filename).lower()
        definers = len(re.findall(r"\bsecurity\s+definer\b", source))
        empty_paths = len(re.findall(r"\bset\s+search_path\s*=\s*''", source))
        assert definers > 0, f"{filename} should define at least one privileged function"
        assert empty_paths == definers, (
            f"{filename}: every SECURITY DEFINER must set search_path = '' "
            f"(found {definers} definers and {empty_paths} fixed paths)"
        )


def test_hardening_migration_revokes_public_execution() -> None:
    source = _normalized("migrate_security_definer_hardening.sql")
    for signature in PRIVILEGED_SIGNATURES:
        assert (
            f"revoke execute on function {signature} "
            "from public, anon, authenticated;"
        ) in source
        assert f"grant execute on function {signature} to service_role;" in source


def test_hardening_migration_uses_qualified_relations_and_bounded_inputs() -> None:
    source = _normalized("migrate_security_definer_hardening.sql")
    for relation in (
        "public.rate_limit_log",
        "public.reviews",
        "public.review_emails",
        "public.handoff_tokens",
    ):
        assert relation in source

    for bound in (
        "char_length(p_ip) > 128",
        "char_length(p_endpoint) > 64",
        "p_window_seconds > 3600",
        "p_max_requests > 1000",
    ):
        assert bound in source

    for endpoint in (
        "'presign'",
        "'submit'",
        "'cancel'",
        "'delete'",
        "'cli-handoff'",
        "'mcp-finalize'",
    ):
        assert endpoint in source


def test_hardening_migration_runs_after_function_creators() -> None:
    migrations = sorted(path.name for path in DEPLOY_DIR.glob("migrate_*.sql"))
    hardening = migrations.index("migrate_security_definer_hardening.sql")
    for creator in (
        "migrate_active_review_capacity.sql",
        "migrate_rate_limit.sql",
        "migrate_rename_handoff_tokens.sql",
    ):
        assert migrations.index(creator) < hardening

