"""Language catalog + resolution for multilingual review output.

Single source of truth for the review-output languages coarse supports, their
human-readable names (what we inject into the LLM directive — models follow
"Simplified Chinese" far more reliably than the code "zh-Hans"), and their text
direction (drives the web render's ``dir`` attribute). The TypeScript mirror is
``web/src/lib/languages.ts``; ``tests/test_web_i18n_contract.py`` guards that
the two stay in sync.

Quotes from the paper always stay in the paper's source language regardless of
any of this — localization only ever affects the reviewer's own prose.
"""

from __future__ import annotations

from coarse.types import LanguageContext

# BCP-47-ish code -> {name, direction}. ``name`` is the human-readable language
# used in the LLM directive; ``direction`` is "ltr"/"rtl" for rendering. Keep in
# sync with web/src/lib/languages.ts (same codes, names, and directions).
SUPPORTED_LANGUAGES: dict[str, dict[str, str]] = {
    "en": {"name": "English", "direction": "ltr"},
    "es": {"name": "Spanish", "direction": "ltr"},
    "fr": {"name": "French", "direction": "ltr"},
    "de": {"name": "German", "direction": "ltr"},
    "nl": {"name": "Dutch", "direction": "ltr"},
    "pt": {"name": "Portuguese", "direction": "ltr"},
    "it": {"name": "Italian", "direction": "ltr"},
    "zh-Hans": {"name": "Simplified Chinese", "direction": "ltr"},
    "zh-Hant": {"name": "Traditional Chinese", "direction": "ltr"},
    "ja": {"name": "Japanese", "direction": "ltr"},
    "ko": {"name": "Korean", "direction": "ltr"},
    "ar": {"name": "Arabic", "direction": "rtl"},
}

_NAME_TO_CODE: dict[str, str] = {
    entry["name"].casefold(): code for code, entry in SUPPORTED_LANGUAGES.items()
}


def normalize_code(code: str | None) -> str:
    """Canonicalize a BCP-47 tag's subtag casing.

    Primary language subtag lowercase, script subtag Title-case (``Hant``),
    region subtag UPPER-case (``BR``; numeric regions unchanged), everything
    else lowercase. Underscores are accepted as separators. Mirror of
    ``normalizeLanguageCode`` in ``web/src/lib/language.ts``.
    """
    if not code:
        return ""
    raw = code.strip().replace("_", "-")
    if not raw:
        return ""
    parts = raw.split("-")
    out: list[str] = []
    for i, part in enumerate(parts):
        if i == 0:
            out.append(part.lower())  # primary language subtag
        elif len(part) == 4 and part.isalpha():
            out.append(part[:1].upper() + part[1:].lower())  # script
        elif len(part) == 2 and part.isalpha():
            out.append(part.upper())  # region (alpha-2)
        else:
            out.append(part.lower())  # numeric region, variants, extensions
    return "-".join(out)


def is_supported(code: str | None) -> bool:
    """Return True if ``code`` (after normalization) is a catalog language."""
    return normalize_code(code) in SUPPORTED_LANGUAGES


def coerce_detected_code(code: str | None) -> str:
    """Best-effort map a model-returned language tag to a supported catalog code.

    Exact (normalized) match wins. Otherwise drop region/variant subtags while
    keeping language+script, so common detector outputs still localize:
    ``pt-BR`` -> ``pt``, ``es-419`` -> ``es``, ``ja-JP`` -> ``ja``,
    ``zh-Hant-HK`` -> ``zh-Hant``. Returns "" if still unmappable — e.g. bare
    ``zh`` is ambiguous between Hans/Hant, so it stays unsupported (English path).
    """
    norm = normalize_code(code)
    if not norm:
        return ""
    if norm in SUPPORTED_LANGUAGES:
        return norm
    parts = norm.split("-")
    if len(parts) >= 2:
        lang_script = "-".join(parts[:2])
        if lang_script in SUPPORTED_LANGUAGES:
            return lang_script
    if parts[0] in SUPPORTED_LANGUAGES:
        return parts[0]
    return ""


def language_name(code: str | None) -> str | None:
    """Map a language code to its human-readable name, or None if unknown/empty."""
    entry = SUPPORTED_LANGUAGES.get(normalize_code(code))
    return entry["name"] if entry else None


def text_direction(code: str | None) -> str:
    """Return 'ltr'/'rtl' for a language code; 'ltr' for unknown/empty."""
    entry = SUPPORTED_LANGUAGES.get(normalize_code(code))
    return entry["direction"] if entry else "ltr"


def _coerce_explicit(value: str) -> tuple[str, str]:
    """Resolve an explicit user value (a code OR a name) to (name, code).

    A supported code or name resolves to the canonical (name, code). An
    unrecognized value is treated as a free-form language name so e.g.
    ``--language Catalan`` still steers the model — returns (value, "") with an
    empty (unknown) code so direction defaults to ltr.
    """
    v = value.strip()
    code = normalize_code(v)
    if code in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[code]["name"], code
    name_match = _NAME_TO_CODE.get(v.casefold())
    if name_match:
        return SUPPORTED_LANGUAGES[name_match]["name"], name_match
    return v, ""


def resolve_language_context(
    *,
    explicit: str | None,
    detected_code: str | None,
    site_code: str | None = None,
) -> tuple[str | None, LanguageContext]:
    """Resolve the effective review-output language.

    Priority: explicit user choice > detected paper language > site language >
    English. Returns ``(directive_name, context)`` where:

    - ``directive_name`` is the human language NAME to inject into the feedback
      agents, or ``None`` for English — including when English is chosen
      explicitly — so the English path is byte-identical to a review with no
      language at all;
    - ``context`` is the :class:`LanguageContext` attached to the ``Review`` and
      persisted. ``paper_language_source`` records how the *effective review
      language* was chosen ("user" = explicit pick, "detected" = followed the
      detected paper language, "default" = site/fallback), which the UI uses to
      label the review ("· auto-detected").

    ``explicit`` may be a code ("es"), a name ("Spanish"), or free-form;
    ``detected_code`` / ``site_code`` are codes. Quotes always stay in the
    paper's source language.
    """
    detected = coerce_detected_code(detected_code)
    site = normalize_code(site_code)

    if explicit and explicit.strip():
        directive_name, review_code = _coerce_explicit(explicit)
        source = "user"
    elif detected and detected != "en":
        directive_name, review_code = language_name(detected), detected
        source = "detected"
    elif site and site != "en":
        directive_name, review_code = language_name(site), site
        source = "default"
    else:
        directive_name, review_code = None, (detected or site or "")
        source = "detected" if detected else "default"

    # English output is the byte-identical default path — no directive even when
    # English is selected explicitly.
    if review_code == "en":
        directive_name = None

    context = LanguageContext(
        site_language=site or "en",
        review_language=review_code,
        paper_language=detected,
        text_direction=text_direction(review_code),
        paper_language_source=source,
    )
    return directive_name, context
