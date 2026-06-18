"""Completeness guard for the site-UI (chrome) i18n catalogs.

There is no JS test runner / local TS build, so this reads the catalog TS
sources verbatim (like tests/test_web_security_invariants.py) and asserts every
locale defines exactly the same message keys as the canonical English catalog,
with the correct exported binding name. A missing/extra key would otherwise only
surface at `next build` time (the `Messages` type enforces it), and a wrong
export name would break the registry import in i18n.ts.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "web/src/lib/i18n"

# locale code -> exported binding name in its catalog file (camelCase where the
# code isn't a valid JS identifier). Must match the imports in web/src/lib/i18n.ts.
LOCALE_EXPORTS = {
    "en": "en",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "nl": "nl",
    "pt": "pt",
    "it": "it",
    "zh-Hans": "zhHans",
    "zh-Hant": "zhHant",
    "ja": "ja",
    "ko": "ko",
    "ar": "ar",
}

_KEY_RE = re.compile(r"^  ([a-zA-Z][a-zA-Z0-9]*):", re.MULTILINE)


def _read(code: str) -> str:
    path = I18N_DIR / f"{code}.ts"
    assert path.exists(), f"missing site-UI catalog: web/src/lib/i18n/{code}.ts"
    return path.read_text(encoding="utf-8")


def _keys(text: str) -> set[str]:
    return set(_KEY_RE.findall(text))


def test_all_locale_catalogs_exist():
    for code in LOCALE_EXPORTS:
        assert (I18N_DIR / f"{code}.ts").exists(), code


def test_english_catalog_has_expected_key_count():
    # 292 keys after the status/review-page localization follow-up (was 139 for
    # the submit page + chrome alone). Guards an accidental key drop in en.
    assert len(_keys(_read("en"))) == 292


def test_every_locale_defines_exactly_the_english_keys():
    english = _keys(_read("en"))
    assert english, "failed to parse any keys from en.ts"
    for code in LOCALE_EXPORTS:
        if code == "en":
            continue
        locale = _keys(_read(code))
        missing = english - locale
        extra = locale - english
        assert not missing, f"{code}.ts is missing keys: {sorted(missing)}"
        assert not extra, f"{code}.ts has unknown keys: {sorted(extra)}"


def test_each_catalog_has_the_correct_export_name():
    for code, binding in LOCALE_EXPORTS.items():
        src = _read(code)
        assert f"export const {binding}: Messages" in src or f"export const {binding} =" in src, (
            f"{code}.ts must export `{binding}` (registry import in i18n.ts depends on it)"
        )


def test_registry_imports_every_locale():
    """i18n.ts must import and register all locale bindings."""
    src = (REPO_ROOT / "web/src/lib/i18n.ts").read_text(encoding="utf-8")
    for binding in LOCALE_EXPORTS.values():
        assert binding in src, f"i18n.ts does not reference the `{binding}` catalog"
