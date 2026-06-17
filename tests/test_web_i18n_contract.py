"""Regression guards for the multilingual API contract (PR-A).

Like tests/test_web_security_invariants.py, these read the TypeScript source
verbatim — the web package has no JS test runner — and assert the load-bearing
wiring is present and correct. They guard the specific mistakes this contract is
prone to:

- The review read SELECT must ADD the language columns WITHOUT dropping
  result_json. A naive port of the stale stranded SELECT omitted result_json,
  which would silently break the structured render + per-comment chat for every
  review on dev.
- BCP-47 casing must be preserved (zh-Hant, pt-BR), not lowercased away.
- Both write routes must validate language input through the shared lib.
- The submit route must forward review_language to the worker, or the choice
  dies in the DB and the worker can never localize.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    path = REPO_ROOT / relative
    assert path.exists(), f"expected {relative} to exist in the repo"
    return path.read_text(encoding="utf-8")


def test_review_select_keeps_result_json_and_adds_language_columns():
    src = _read("web/src/app/api/review/[id]/route.ts")
    # result_json must survive — the structured render + per-comment chat read it;
    # a SELECT that drops it silently degrades every review page to a raw dump.
    assert "result_json" in src, "review SELECT must still fetch result_json"
    for col in (
        "site_language",
        "review_language",
        "paper_language",
        "paper_language_source",
        "text_direction",
        "taxonomy",
    ):
        assert col in src, f"review SELECT is missing the {col} column"


def test_language_helper_preserves_bcp47_casing():
    src = _read("web/src/lib/language.ts")
    # The buggy original lowercased the entire tag, mangling zh-Hant / pt-BR.
    assert 'value.trim().replace(/_/g, "-").toLowerCase()' not in src, (
        "normalizeLanguageCode must not lowercase the whole tag — that mangles "
        "BCP-47 script/region subtags (zh-Hant -> zh-hant)."
    )
    # Per-subtag canonicalization: language lowercase, region UPPER-case.
    assert ".toLowerCase()" in src, "language subtag must still be lower-cased"
    assert ".toUpperCase()" in src, "region subtags must be upper-cased"


def test_both_write_routes_validate_language_via_shared_lib():
    for route in (
        "web/src/app/api/submit/route.ts",
        "web/src/app/api/mcp-finalize/route.ts",
    ):
        src = _read(route)
        assert "@/lib/language" in src, f"{route} must import the shared language lib"
        assert "validateLanguageFields" in src, f"{route} must validate language fields"


def test_submit_forwards_review_language_to_worker():
    src = _read("web/src/app/api/submit/route.ts")
    # The worker can only localize if the web forwards the choice. Guard the
    # transport so a refactor can't silently strand the language in the DB.
    assert "review_language:" in src, (
        "submit route must forward review_language in the Modal trigger body"
    )
