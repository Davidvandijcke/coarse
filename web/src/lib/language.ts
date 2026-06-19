// Shared multilingual contract helpers — the single source of truth for the
// submit and finalize routes (see docs/MULTILINGUAL_PLAN.md). Validation +
// BCP-47 normalization only; the code↔human-name catalog used to instruct the
// model (e.g. "fr" → "French") lands with PR-B.

export const LANGUAGE_CODE_RE = /^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/i;
export const TEXT_DIRECTIONS = new Set(["ltr", "rtl"]);
export const PAPER_LANGUAGE_SOURCES = new Set(["detected", "user", "default"]);

/**
 * Canonicalize a BCP-47 tag's subtag casing: primary language lowercase,
 * script subtag Title-case (4 letters → `Hant`), region subtag UPPER-case
 * (2 letters → `BR`; numeric regions like `419` unchanged), variants/extensions
 * lowercase. Returns "" for non-strings / empty input. Underscores are accepted
 * as separators and normalized to hyphens.
 *
 * Fixes the original contract draft, which lowercased the whole tag and so
 * mangled `zh-Hant` → `zh-hant` and `pt-BR` → `pt-br`.
 */
export function normalizeLanguageCode(value: unknown): string {
  if (typeof value !== "string") return "";
  const raw = value.trim().replace(/_/g, "-");
  if (!raw) return "";
  return raw
    .split("-")
    .map((part, i) => {
      if (i === 0) return part.toLowerCase(); // primary language subtag
      if (/^[A-Za-z]{4}$/.test(part)) {
        return part[0].toUpperCase() + part.slice(1).toLowerCase(); // script
      }
      if (/^[A-Za-z]{2}$/.test(part)) return part.toUpperCase(); // region (alpha-2)
      return part.toLowerCase(); // numeric region, variants, extensions
    })
    .join("-");
}

export function normalizeTextDirection(value: unknown): string {
  if (typeof value !== "string") return "";
  return value.trim().toLowerCase();
}

export interface LanguageFields {
  site_language: string;
  review_language: string;
  paper_language: string;
  paper_language_source: string;
  text_direction: string;
}

/** Parse + normalize the optional language fields from a request body. */
export function parseLanguageFields(body: Record<string, unknown>): LanguageFields {
  return {
    site_language: normalizeLanguageCode(body.site_language),
    review_language: normalizeLanguageCode(body.review_language),
    paper_language: normalizeLanguageCode(body.paper_language),
    paper_language_source:
      typeof body.paper_language_source === "string"
        ? body.paper_language_source.trim().toLowerCase()
        : "",
    text_direction: normalizeTextDirection(body.text_direction),
  };
}

/**
 * Returns an error string naming the first malformed language field, or null
 * if all (possibly empty) fields are valid. Empty fields are always valid —
 * the whole contract is optional.
 */
export function validateLanguageFields(f: LanguageFields): string | null {
  for (const field of ["site_language", "review_language", "paper_language"] as const) {
    const value = f[field];
    if (value && !LANGUAGE_CODE_RE.test(value)) return `Invalid ${field}`;
  }
  if (f.text_direction && !TEXT_DIRECTIONS.has(f.text_direction)) {
    return "Invalid text_direction";
  }
  if (f.paper_language_source && !PAPER_LANGUAGE_SOURCES.has(f.paper_language_source)) {
    return "Invalid paper_language_source";
  }
  return null;
}

/** Build a DB-update fragment of only the non-empty language fields. */
export function languageUpdateFields(f: LanguageFields): Record<string, string> {
  const out: Record<string, string> = {};
  if (f.site_language) out.site_language = f.site_language;
  if (f.review_language) out.review_language = f.review_language;
  if (f.paper_language) out.paper_language = f.paper_language;
  if (f.paper_language_source) out.paper_language_source = f.paper_language_source;
  if (f.text_direction) out.text_direction = f.text_direction;
  return out;
}
