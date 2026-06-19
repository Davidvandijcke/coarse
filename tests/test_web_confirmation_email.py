"""Completeness guard for the localized submit-time confirmation email.

No JS test runner, so read the TS source verbatim (like test_web_site_i18n.py).
TypeScript's ``Record<string, ConfirmationEmailCopy>`` already enforces that every
locale entry has all keys at build time, but it does NOT catch a *missing locale*
(``confirmationEmailCopy`` silently falls back to English) or a translation that
dropped a ``{title}`` / ``{model}`` placeholder the submit route substitutes.
Guard both here. The locale set mirrors the review-language catalog.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "web/src/lib/confirmationEmail.ts"

# Same set as web/src/lib/i18n.ts / languages.ts.
LOCALES = ["en", "es", "fr", "de", "nl", "pt", "it", "zh-Hans", "zh-Hant", "ja", "ko", "ar"]


def _src() -> str:
    assert SRC.exists(), "missing web/src/lib/confirmationEmail.ts"
    return SRC.read_text(encoding="utf-8")


def test_all_locales_present():
    text = _src()
    assert "en: EN" in text, "English base (en: EN) missing from CATALOG"
    for code in LOCALES:
        if code == "en":
            continue
        token = f'"{code}":' if "-" in code else f"{code}: {{"
        assert token in text, f"confirmation email missing locale {code}"


def test_placeholders_preserved():
    # Count only inside the template-literal value lines (backtick lines) so the
    # interface's documentation comments don't inflate the totals.
    value_lines = "\n".join(ln for ln in _src().splitlines() if "`" in ln)
    # {model} appears once per locale (in `body`): 12 locales.
    assert value_lines.count("{model}") == 12, value_lines.count("{model}")
    # {title} appears in subject + body + bodyNoModel: 3 × 12 locales.
    assert value_lines.count("{title}") == 36, value_lines.count("{title}")
