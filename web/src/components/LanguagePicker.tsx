"use client";

import { SUPPORTED_LANGUAGES } from "@/lib/languages";

/* ── Review-language picker ────────────────────────────────────
 * Presentational dropdown that mirrors ModelPicker's label styling.
 * The default option (value "") means "auto" — match the paper's own
 * language — and is the invariant that keeps the submit body and the
 * handoff command byte-identical to the pre-i18n behavior.
 */
export default function LanguagePicker({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (code: string) => void;
  disabled?: boolean;
}) {
  return (
    <div>
      <span
        style={{
          display: "block",
          fontFamily: "var(--font-chalk)",
          fontSize: "1.15rem",
          color: "var(--dust)",
          marginBottom: "0.5rem",
        }}
      >
        Review language
      </span>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        aria-label="Review language"
        style={{
          padding: "0.4rem 0.85rem",
          background: "var(--board-surface)",
          color: "var(--chalk)",
          border: "1px solid var(--tray)",
          borderRadius: "2px",
          fontFamily: "var(--font-space-mono), monospace",
          fontSize: "1.1rem",
          cursor: disabled ? "not-allowed" : "pointer",
          opacity: disabled ? 0.55 : 1,
        }}
      >
        <option value="">Auto — match the paper&apos;s language</option>
        {SUPPORTED_LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>

      <p
        style={{
          fontFamily: "var(--font-chalk)",
          fontSize: "1rem",
          color: "var(--dust)",
          marginTop: "0.4rem",
        }}
      >
        Defaults to the paper&apos;s own language; quotes always stay in the
        original.
      </p>
    </div>
  );
}
