// Single source of truth for the review-output languages the web UI offers,
// their human-readable names, and text direction. Mirror of
// src/coarse/languages.py (same codes, names, directions, order) —
// tests/test_web_i18n_contract.py guards that the two stay in sync.

export interface LanguageEntry {
  code: string;
  name: string;
  direction: "ltr" | "rtl";
}

export const SUPPORTED_LANGUAGES: LanguageEntry[] = [
  { code: "en", name: "English", direction: "ltr" },
  { code: "es", name: "Spanish", direction: "ltr" },
  { code: "fr", name: "French", direction: "ltr" },
  { code: "de", name: "German", direction: "ltr" },
  { code: "nl", name: "Dutch", direction: "ltr" },
  { code: "pt", name: "Portuguese", direction: "ltr" },
  { code: "it", name: "Italian", direction: "ltr" },
  { code: "zh-Hans", name: "Simplified Chinese", direction: "ltr" },
  { code: "zh-Hant", name: "Traditional Chinese", direction: "ltr" },
  { code: "ja", name: "Japanese", direction: "ltr" },
  { code: "ko", name: "Korean", direction: "ltr" },
  { code: "ar", name: "Arabic", direction: "rtl" },
];

const BY_CODE = new Map(SUPPORTED_LANGUAGES.map((l) => [l.code, l]));

/** Human-readable name for a language code, or null if unknown/empty. */
export function languageName(code: string | null | undefined): string | null {
  if (!code) return null;
  return BY_CODE.get(code)?.name ?? null;
}

/** Text direction for a language code; "ltr" for unknown/empty. */
export function textDirection(code: string | null | undefined): "ltr" | "rtl" {
  if (!code) return "ltr";
  return BY_CODE.get(code)?.direction ?? "ltr";
}
