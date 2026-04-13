"""Regression guards for web handoff lifetime/cleanup behavior."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_cli_handoff_uses_three_hour_finalize_token() -> None:
    text = _read("web/src/app/api/cli-handoff/route.ts")
    assert "const FINALIZE_TOKEN_TTL_MINUTES = 180;" in text


def test_mcp_handoff_uses_three_hour_state_and_finalize_ttls() -> None:
    text = _read("web/src/app/api/mcp-handoff/route.ts")
    assert "const HANDOFF_TTL_MINUTES = 180;" in text
    assert "const STATE_TTL_SECONDS = HANDOFF_TTL_MINUTES * 60;" in text
    assert "const FINALIZE_TOKEN_TTL_MINUTES = HANDOFF_TTL_MINUTES;" in text


def test_handoff_download_url_uses_three_hour_ttl() -> None:
    text = _read("web/src/app/h/[token]/route.ts")
    assert "const PDF_SIGNED_URL_TTL_SECONDS = 3 * 60 * 60;" in text
    assert "Token valid for 3 hours." in text


def test_finalize_route_deletes_source_and_state_blob() -> None:
    text = _read("web/src/app/api/mcp-finalize/route.ts")
    assert "const storageObjects = [`${paperId}.mcp.json`];" in text
    assert "storageObjects.unshift(`${paperId}${sourceExt}`);" in text
    assert 'await supabase.storage.from("papers").remove(storageObjects);' in text


def test_presign_and_followup_routes_require_handoff_secret() -> None:
    presign = _read("web/src/app/api/presign/route.ts")
    submit = _read("web/src/app/api/submit/route.ts")
    cli_handoff = _read("web/src/app/api/cli-handoff/route.ts")
    mcp_extract = _read("web/src/app/api/mcp-extract/route.ts")
    mcp_handoff = _read("web/src/app/api/mcp-handoff/route.ts")

    assert 'from("review_handoff_secrets")' in presign
    assert "handoffSecret" in presign
    assert "consumeReviewHandoffSecret" in submit
    assert "consumeReviewHandoffSecret" in cli_handoff
    assert "requireReviewHandoffSecret" in mcp_extract
    assert "consumeReviewHandoffSecret" in mcp_handoff


def test_success_paths_consume_handoff_secret() -> None:
    submit = _read("web/src/app/api/submit/route.ts")
    cli_handoff = _read("web/src/app/api/cli-handoff/route.ts")
    mcp_handoff = _read("web/src/app/api/mcp-handoff/route.ts")
    finalize = _read("web/src/app/api/mcp-finalize/route.ts")

    assert "consumeReviewHandoffSecret(supabaseAdmin, id, handoffSecret)" in submit
    assert "consumeReviewHandoffSecret(supabase, paperId, handoffSecret)" in cli_handoff
    assert "consumeReviewHandoffSecret(supabase, paperId, handoffSecret)" in mcp_handoff
    assert 'from("review_handoff_secrets").delete().eq("review_id", paperId);' in finalize
