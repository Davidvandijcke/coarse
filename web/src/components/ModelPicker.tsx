"use client";

import { useState, useEffect, useRef, useCallback } from "react";

import { formatPromptPrice } from "@/lib/estimateCost";
import { useSiteLanguageContext } from "@/lib/i18n";

/* ── Default model options ─────────────────────────────────── */
type DefaultModel = {
  id: string;
  label: string;
  provider: string;
  /** Render greyed-out and non-selectable (model temporarily unavailable). */
  unavailable?: boolean;
  /** Append a smaller "(provider)" suffix to the chip, e.g. "Fusion (OpenRouter)". */
  showProvider?: boolean;
};

const DEFAULT_MODELS: DefaultModel[] = [
  { id: "anthropic/claude-fable-5", label: "Fable 5", provider: "Anthropic" },
  { id: "anthropic/claude-opus-4.8", label: "Opus 4.8", provider: "Anthropic" },
  { id: "anthropic/claude-sonnet-4.6", label: "Sonnet 4.6", provider: "Anthropic" },
  { id: "openai/gpt-5.5", label: "GPT-5.5", provider: "OpenAI" },
  { id: "openai/gpt-5-mini", label: "GPT-5 Mini", provider: "OpenAI" },
  { id: "google/gemini-3.1-pro-preview", label: "Gemini 3.1 Pro", provider: "Google" },
  { id: "google/gemini-3.5-flash", label: "Gemini 3.5 Flash", provider: "Google" },
  { id: "qwen/qwen3.7-plus", label: "Qwen 3.7 Plus", provider: "Qwen" },
  { id: "moonshotai/kimi-k2.6", label: "Kimi K2.6", provider: "Moonshot" },
  { id: "deepseek/deepseek-v4-pro", label: "DeepSeek V4", provider: "DeepSeek" },
  { id: "x-ai/grok-4.3", label: "Grok 4.3", provider: "xAI" },
  { id: "meta-llama/llama-4-maverick", label: "Llama 4 Maverick", provider: "Meta" },
  { id: "z-ai/glm-5.2", label: "GLM 5.2", provider: "Z.ai" },
  // OpenRouter Fusion: a multi-model deliberation panel with web search.
  // Higher latency and variable (usage-based) cost than a single model — see
  // the FUSION_MODEL note in src/coarse/models.py. showProvider tags the chip
  // "(OpenRouter)" since "Fusion" alone is less self-explanatory than e.g. "Opus 4.8".
  { id: "openrouter/fusion", label: "Fusion", provider: "OpenRouter", showProvider: true },
];

interface OpenRouterModel {
  id: string;
  name: string;
  pricing?: { prompt?: string; completion?: string };
  context_length?: number;
}

/* ── Search modal ──────────────────────────────────────────── */
function SearchModal({
  onSelect,
  onClose,
}: {
  onSelect: (id: string, label: string) => void;
  onClose: () => void;
}) {
  const { t } = useSiteLanguageContext();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<OpenRouterModel[]>([]);
  const [allModels, setAllModels] = useState<OpenRouterModel[]>([]);
  const [loading, setLoading] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Fetch OpenRouter model list once
  useEffect(() => {
    fetch("https://openrouter.ai/api/v1/models")
      .then((r) => r.json())
      .then((data) => {
        const models: OpenRouterModel[] = (data.data || [])
          .filter((m: OpenRouterModel) => m.id && m.name)
          .sort((a: OpenRouterModel, b: OpenRouterModel) => a.name.localeCompare(b.name));
        setAllModels(models);
        setResults(models.slice(0, 30));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!query.trim()) {
      setResults(allModels.slice(0, 30));
      return;
    }
    const q = query.toLowerCase();
    setResults(
      allModels
        .filter((m) => m.id.toLowerCase().includes(q) || m.name.toLowerCase().includes(q))
        .slice(0, 30)
    );
  }, [query, allModels]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  function formatPrice(model: OpenRouterModel): string {
    const p = model.pricing;
    if (!p?.prompt) return "";
    // Shared with the cost estimator: shows "variable" for dynamic ("-1")
    // prices, "free" for 0, "$X/M" otherwise.
    return formatPromptPrice(parseFloat(p.prompt));
  }

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0,0,0,0.6)",
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          background: "var(--board-surface)",
          border: "1px solid var(--tray)",
          borderRadius: "4px",
          width: "min(560px, 90vw)",
          maxHeight: "70vh",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Search input */}
        <div style={{ padding: "1.25rem 1.25rem 0.75rem" }}>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("modelPickerSearchPlaceholder")}
            className="field-line-mono"
            style={{ width: "100%", fontSize: "1rem" }}
          />
        </div>

        {/* Results */}
        <div style={{ overflowY: "auto", flex: 1, padding: "0 0.5rem 0.75rem" }}>
          {loading ? (
            <p
              style={{
                padding: "2rem",
                textAlign: "center",
                fontFamily: "var(--font-chalk)",
                color: "var(--dust)",
                fontSize: "1.1rem",
              }}
            >
              {t("modelPickerLoading")}
            </p>
          ) : results.length === 0 ? (
            <p
              style={{
                padding: "2rem",
                textAlign: "center",
                fontFamily: "var(--font-chalk)",
                color: "var(--dust)",
                fontSize: "1.1rem",
              }}
            >
              {t("modelPickerNoResults")}
            </p>
          ) : (
            results.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => {
                  onSelect(m.id, m.name);
                  onClose();
                }}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "baseline",
                  width: "100%",
                  padding: "0.6rem 0.75rem",
                  background: "transparent",
                  border: "none",
                  borderRadius: "2px",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background 0.15s",
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.background = "var(--tray)")
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.background = "transparent")
                }
              >
                <span>
                  <span
                    style={{
                      fontFamily: "var(--font-space-mono), monospace",
                      fontSize: "1rem",
                      color: "var(--chalk-bright)",
                    }}
                  >
                    {m.name}
                  </span>
                  <span
                    style={{
                      fontFamily: "var(--font-space-mono), monospace",
                      fontSize: "1.05rem",
                      color: "var(--dust)",
                      marginLeft: "0.5rem",
                    }}
                  >
                    {m.id}
                  </span>
                </span>
                <span
                  style={{
                    fontFamily: "var(--font-space-mono), monospace",
                    fontSize: "1.05rem",
                    color: "var(--dust)",
                    whiteSpace: "nowrap",
                    marginLeft: "1rem",
                  }}
                >
                  {formatPrice(m)}
                </span>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Main ModelPicker component ────────────────────────────── */
export default function ModelPicker({
  value,
  onChange,
}: {
  value: string;
  onChange: (modelId: string) => void;
}) {
  const { t } = useSiteLanguageContext();
  const [showSearch, setShowSearch] = useState(false);
  const [customLabel, setCustomLabel] = useState<string | null>(null);

  const isDefault = DEFAULT_MODELS.some((m) => m.id === value);
  const displayLabel =
    customLabel && !isDefault
      ? customLabel
      : DEFAULT_MODELS.find((m) => m.id === value)?.label ?? value;

  const handleSearchSelect = useCallback(
    (id: string, label: string) => {
      onChange(id);
      setCustomLabel(label);
    },
    [onChange]
  );

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
        {t("modelPickerLabel")}
      </span>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        {DEFAULT_MODELS.map((m) => {
          const selected = value === m.id;
          const unavailable = m.unavailable === true;
          return (
            <button
              key={m.id}
              type="button"
              disabled={unavailable}
              title={unavailable ? t("modelPickerUnavailableTitle") : undefined}
              onClick={() => {
                if (unavailable) return;
                onChange(m.id);
                setCustomLabel(null);
              }}
              style={{
                padding: "0.4rem 0.85rem",
                background: selected ? "var(--yellow-chalk)" : "var(--board-surface)",
                color: unavailable ? "var(--dust)" : selected ? "var(--board)" : "var(--chalk)",
                border: `1px solid ${selected ? "var(--yellow-chalk)" : "var(--tray)"}`,
                borderRadius: "2px",
                fontFamily: "var(--font-space-mono), monospace",
                fontSize: "1.1rem",
                cursor: unavailable ? "not-allowed" : "pointer",
                opacity: unavailable ? 0.45 : 1,
                transition: "all 0.15s",
                whiteSpace: "nowrap",
              }}
            >
              {m.label}
              {m.showProvider && (
                <span style={{ fontSize: "0.78em", opacity: 0.7, marginLeft: "0.3rem" }}>
                  ({m.provider})
                </span>
              )}
            </button>
          );
        })}

        <button
          type="button"
          onClick={() => setShowSearch(true)}
          style={{
            padding: "0.4rem 0.85rem",
            background: !isDefault && value ? "var(--yellow-chalk)" : "transparent",
            color: !isDefault && value ? "var(--board)" : "var(--blue-chalk)",
            border: `1px solid ${!isDefault && value ? "var(--yellow-chalk)" : "var(--tray)"}`,
            borderRadius: "2px",
            fontFamily: "var(--font-space-mono), monospace",
            fontSize: "1.1rem",
            cursor: "pointer",
            transition: "all 0.15s",
            whiteSpace: "nowrap",
          }}
        >
          {!isDefault && value ? displayLabel : t("modelPickerSearch")}
        </button>
      </div>

      {showSearch && (
        <SearchModal
          onSelect={handleSearchSelect}
          onClose={() => setShowSearch(false)}
        />
      )}
    </div>
  );
}
