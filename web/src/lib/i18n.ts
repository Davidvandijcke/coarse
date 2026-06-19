// Lightweight site-UI internationalization (no framework dependency).
//
// Distinct from the *review* language (what the AI writes the review in): this
// is the website chrome. Default is always English; the user switches manually
// via SiteLanguageSwitcher and the choice is persisted in localStorage. The
// supported locale set mirrors the review-language catalog (languages.ts).
//
// The English catalog (./i18n/en) is the canonical source of message keys and
// the `Messages` type; every other locale catalog must satisfy `Messages`, so a
// missing or misspelled key is a compile error. New reviews render from
// result_json, so this layer only affects the static site chrome.

"use client";

import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { SUPPORTED_LANGUAGES, textDirection } from "@/lib/languages";
import { en } from "@/lib/i18n/en";
import { es } from "@/lib/i18n/es";
import { fr } from "@/lib/i18n/fr";
import { de } from "@/lib/i18n/de";
import { nl } from "@/lib/i18n/nl";
import { pt } from "@/lib/i18n/pt";
import { it } from "@/lib/i18n/it";
import { zhHans } from "@/lib/i18n/zh-Hans";
import { zhHant } from "@/lib/i18n/zh-Hant";
import { ja } from "@/lib/i18n/ja";
import { ko } from "@/lib/i18n/ko";
import { ar } from "@/lib/i18n/ar";

/** The canonical message keys — derived from the English catalog. A locale
 * catalog must define exactly these keys (missing/misspelled = compile error)
 * with plain string values (translated text, so not the English literal types). */
export type MessageKey = keyof typeof en;
export type Messages = Record<MessageKey, string>;

/** Supported site-UI locale codes (same set as the review-language catalog). */
export type SiteLocale =
  | "en"
  | "es"
  | "fr"
  | "de"
  | "nl"
  | "pt"
  | "it"
  | "zh-Hans"
  | "zh-Hant"
  | "ja"
  | "ko"
  | "ar";

const CATALOGS: Record<SiteLocale, Messages> = {
  en,
  es,
  fr,
  de,
  nl,
  pt,
  it,
  "zh-Hans": zhHans,
  "zh-Hant": zhHant,
  ja,
  ko,
  ar,
};

/** The locales offered in the switcher, in catalog order (en first). */
export const SITE_LOCALES: { code: SiteLocale; name: string }[] = SUPPORTED_LANGUAGES.filter(
  (l): l is (typeof SUPPORTED_LANGUAGES)[number] & { code: SiteLocale } => l.code in CATALOGS,
).map((l) => ({ code: l.code as SiteLocale, name: l.name }));

const STORAGE_KEY = "coarse_site_language";
const DEFAULT_LOCALE: SiteLocale = "en";

function isSiteLocale(value: string | null): value is SiteLocale {
  return value != null && value in CATALOGS;
}

/** Return the messages for a locale (English fallback for an unknown code). */
export function messagesFor(locale: SiteLocale): Messages {
  return CATALOGS[locale] ?? en;
}

/**
 * Map a stored/BCP-47 language code to a supported site locale, or null.
 * Accepts exact catalog codes ("nl", "zh-Hant") and falls back to the base
 * language for region/script variants ("pt-BR" → "pt", bare "zh" → "zh-Hans").
 * Used to render a review in the language it was created in.
 */
export function coerceSiteLocale(value: string | null | undefined): SiteLocale | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (trimmed in CATALOGS) return trimmed as SiteLocale;
  const base = trimmed.split("-")[0].toLowerCase();
  if (base === "zh") return "zh-Hans";
  if (base in CATALOGS) return base as SiteLocale;
  return null;
}

/**
 * Site-language state: persisted in localStorage, default English (no browser
 * auto-detect), and applies `lang`/`dir` to <html> so the whole page chrome
 * flips to RTL when the UI language is Arabic. Returns the current locale, a
 * setter, and a bound translator `t`.
 */
export function useSiteLanguage(): {
  locale: SiteLocale;
  setLocale: (l: SiteLocale) => void;
  applyInitialLocale: (l: SiteLocale) => void;
  t: (key: MessageKey) => string;
} {
  const [locale, setLocaleState] = useState<SiteLocale>(DEFAULT_LOCALE);
  // Whether the visitor has an explicit language choice this session (a stored
  // preference or a switcher click). Once true, a page-scoped initial locale
  // (e.g. a review's stored language) must not override it.
  const userChoseRef = useRef(false);

  // Restore persisted choice on mount (client-only; SSR renders English).
  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (isSiteLocale(stored)) {
        userChoseRef.current = true;
        setLocaleState(stored);
      }
    } catch {
      // localStorage unavailable (private mode etc.) — stay on default.
    }
  }, []);

  // Reflect the locale onto <html lang>/<dir> whenever it changes.
  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = textDirection(locale);
    return () => {
      // Leave attributes as-is on unmount; the next page sets them.
    };
  }, [locale]);

  const setLocale = useCallback((l: SiteLocale) => {
    userChoseRef.current = true;
    setLocaleState(l);
    try {
      window.localStorage.setItem(STORAGE_KEY, l);
    } catch {
      // Best-effort persistence only.
    }
  }, []);

  // Apply a page-scoped initial locale (e.g. the language a review was created
  // in) WITHOUT persisting it as the visitor's global preference, and only if
  // the visitor hasn't already chosen one. Lets a review opened from an email
  // link on a fresh device render in the review's language, not English.
  const applyInitialLocale = useCallback((l: SiteLocale) => {
    if (userChoseRef.current) return;
    setLocaleState(l);
  }, []);

  const t = useCallback((key: MessageKey) => messagesFor(locale)[key] ?? en[key], [locale]);

  return { locale, setLocale, applyInitialLocale, t };
}

// --- Context so the switcher and the page share one locale state ---

type SiteLanguageValue = ReturnType<typeof useSiteLanguage>;

const SiteLanguageContext = createContext<SiteLanguageValue | null>(null);

/** Wrap the (client) page so descendants share one site-language state. */
export function SiteLanguageProvider({ children }: { children: ReactNode }) {
  const value = useSiteLanguage();
  return createElement(SiteLanguageContext.Provider, { value }, children);
}

/**
 * Access the shared site-language state. Falls back to a standalone English
 * binding if used outside a provider, so a component never crashes.
 */
export function useSiteLanguageContext(): SiteLanguageValue {
  const ctx = useContext(SiteLanguageContext);
  if (ctx) return ctx;
  return {
    locale: DEFAULT_LOCALE,
    setLocale: () => {},
    applyInitialLocale: () => {},
    t: (key: MessageKey) => en[key],
  };
}
