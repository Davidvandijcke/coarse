"use client";

import { SITE_LOCALES, useSiteLanguageContext } from "@/lib/i18n";

/* ── Site-UI language switcher ──────────────────────────────────
 * Compact dropdown for the website chrome language (distinct from the
 * review-output language picker on the form). Defaults to English; the
 * choice is persisted in localStorage by the shared context. Place in
 * the page header.
 */
export default function SiteLanguageSwitcher() {
  const { locale, setLocale, t } = useSiteLanguageContext();

  return (
    <select
      value={locale}
      onChange={(e) => setLocale(e.target.value as typeof locale)}
      aria-label={t("siteLanguageLabel")}
      title={t("siteLanguageLabel")}
      style={{
        padding: "0.25rem 0.5rem",
        background: "var(--board-surface)",
        color: "var(--chalk)",
        border: "1px solid var(--tray)",
        borderRadius: "2px",
        fontFamily: "var(--font-space-mono), monospace",
        fontSize: "0.95rem",
        cursor: "pointer",
      }}
    >
      {SITE_LOCALES.map((l) => (
        <option key={l.code} value={l.code}>
          {l.name}
        </option>
      ))}
    </select>
  );
}
