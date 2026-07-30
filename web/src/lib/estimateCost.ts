/**
 * Client-side cost estimation for coarse reviews.
 *
 * Shared stage heuristics are generated from src/coarse/pipeline_spec.py into
 * web/src/data/pipelineSpec.json. Dynamic assembly still happens here, but the
 * section caps, stage budgets, and reasoning-model rules come from the same
 * source as the Python estimator.
 *
 * Token estimate: extract text via pdf.js (loaded from CDN to avoid webpack issues).
 * Pricing: fetched from OpenRouter /api/v1/models.
 */

import pipelineSpec from "../data/pipelineSpec.json" with { type: "json" };

const PDFJS_CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.9.155/pdf.min.mjs";
const PDFJS_WORKER_CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.9.155/pdf.worker.min.mjs";

/** Per-token pricing (USD) from OpenRouter /api/v1/models */
export interface ModelPricing {
  promptCostPerToken: number;
  completionCostPerToken: number;
  pricingTiers?: ModelPricingTier[];
}

export interface ModelPricingTier {
  minPromptTokens: number;
  promptCostPerToken: number;
  completionCostPerToken: number;
}

/**
 * Representative per-token rates for models OpenRouter reports as dynamic
 * (prompt/completion = "-1"), e.g. openrouter/fusion. Shared from
 * pipeline_spec.py via pipelineSpec.json so the web and Python estimators
 * can't drift. Used to override the -1 sentinel, which would otherwise make
 * the review-cost estimate go negative.
 */
const DYNAMIC_PRICING_OVERRIDES = pipelineSpec.dynamicPricingOverrides as Record<
  string,
  { prompt: number; completion: number }
>;

let pricingCache: Map<string, ModelPricing> | null = null;

/** Fetch and cache the full OpenRouter pricing map. */
async function fetchPricingMap(): Promise<Map<string, ModelPricing>> {
  if (pricingCache) return pricingCache;
  // 10s timeout so a hung openrouter.ai upstream does not pin a Vercel
  // function slot indefinitely. Matches the pattern used by every
  // other server→upstream fetch in the web surface (turnstile.ts,
  // submit/route.ts).
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10_000);
  let resp: Response;
  try {
    resp = await fetch("https://openrouter.ai/api/v1/models", {
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }
  const data = await resp.json();
  const map = new Map<string, ModelPricing>();
  for (const m of data.data ?? []) {
    if (!m.id || !m.pricing?.prompt) continue;
    const promptCostPerToken = parseFloat(m.pricing.prompt);
    const completionCostPerToken = parseFloat(m.pricing.completion ?? "0");
    // OpenRouter reports a negative price ("-1") for dynamic-priced models —
    // ones whose per-request cost depends on which models the request fans
    // out to (e.g. openrouter/fusion, openrouter/auto). Left as-is, the
    // negative rate makes the review-cost estimate go negative. So:
    //   - substitute representative rates if we have them (Fusion), else
    //   - omit the model, so getModelPricing() returns null and the UI shows
    //     "cost estimate unavailable" instead of a negative dollar figure.
    if (promptCostPerToken < 0 || completionCostPerToken < 0) {
      const override = DYNAMIC_PRICING_OVERRIDES[m.id];
      if (override) {
        map.set(m.id, {
          promptCostPerToken: override.prompt,
          completionCostPerToken: override.completion,
        });
      }
      continue;
    }
    const pricingTiers: ModelPricingTier[] = Array.isArray(m.pricing.overrides)
      ? m.pricing.overrides
          .map((tier: Record<string, unknown>) => ({
            minPromptTokens: Number(tier.min_prompt_tokens),
            promptCostPerToken: Number(tier.prompt),
            completionCostPerToken: Number(tier.completion),
          }))
          .filter(
            (tier: ModelPricingTier) =>
              Number.isFinite(tier.minPromptTokens) &&
              tier.minPromptTokens > 0 &&
              Number.isFinite(tier.promptCostPerToken) &&
              tier.promptCostPerToken >= 0 &&
              Number.isFinite(tier.completionCostPerToken) &&
              tier.completionCostPerToken >= 0,
          )
          .sort(
            (left: ModelPricingTier, right: ModelPricingTier) =>
              left.minPromptTokens - right.minPromptTokens,
          )
      : [];
    map.set(m.id, {
      promptCostPerToken,
      completionCostPerToken,
      ...(pricingTiers.length > 0 ? { pricingTiers } : {}),
    });
  }
  pricingCache = map;
  return map;
}

/**
 * Format a per-token prompt price (USD) as a compact "$X/M" chip label.
 * Returns "variable" for dynamic (negative) rates, "free" for 0, and "" for
 * unknown/NaN. Kept here (not in ModelPicker) so it's unit-testable and so
 * price formatting lives next to the pricing types.
 */
export function formatPromptPrice(promptCostPerToken: number | null | undefined): string {
  if (promptCostPerToken == null || Number.isNaN(promptCostPerToken)) return "";
  const perMillion = promptCostPerToken * 1_000_000;
  if (perMillion < 0) return "variable";
  if (perMillion === 0) return "free";
  if (perMillion < 1) return `$${perMillion.toFixed(2)}/M`;
  return `$${perMillion.toFixed(0)}/M`;
}

export async function getModelPricing(modelId: string): Promise<ModelPricing | null> {
  const map = await fetchPricingMap();
  return map.get(modelId) ?? null;
}

/**
 * True for characters from spaceless CJK scripts (Han / Kana / Hangul), which
 * pack ~1-1.5 tokens per character instead of Latin's ~4. Mirrors
 * `textscript._is_cjk_char` in the Python source so the web and CLI token
 * estimates agree on CJK papers.
 */
function isCjkCodePoint(cp: number): boolean {
  return (
    (cp >= 0x3040 && cp <= 0x30ff) || // Hiragana + Katakana
    (cp >= 0x3400 && cp <= 0x4dbf) || // CJK Unified Ext A
    (cp >= 0x4e00 && cp <= 0x9fff) || // CJK Unified Ideographs
    (cp >= 0xf900 && cp <= 0xfaff) || // CJK Compatibility Ideographs
    (cp >= 0xac00 && cp <= 0xd7a3) || // Hangul syllables
    (cp >= 0x20000 && cp <= 0x2fa1f) // CJK Unified Ext B+ (supplementary)
  );
}

/**
 * Script-aware token estimate, mirroring `textscript.estimate_tokens`:
 * CJK characters at ~1.6 chars/token, everything else at ~4 chars/token. For
 * pure-Latin text this equals `Math.floor(text.length / 4)`, so English cost
 * quotes are unchanged; CJK papers estimate materially higher instead of being
 * under-counted ~4-6x.
 *
 * Iterates code points (for...of) so supplementary-plane ideographs count as
 * one CJK character, matching Python's per-character iteration.
 */
export function estimateTokensFromString(text: string): number {
  let cjk = 0;
  let other = 0;
  for (const ch of text) {
    if (isCjkCodePoint(ch.codePointAt(0)!)) cjk++;
    else other++;
  }
  return Math.floor(cjk / 1.6 + other / 4);
}

/* eslint-disable @typescript-eslint/no-explicit-any */
let pdfjsPromise: Promise<any> | null = null;

/** Load pdf.js from CDN (bypasses webpack bundling entirely). */
function loadPdfJs(): Promise<any> {
  if (pdfjsPromise) return pdfjsPromise;
  pdfjsPromise = import(/* webpackIgnore: true */ PDFJS_CDN).then((mod) => {
    mod.GlobalWorkerOptions.workerSrc = PDFJS_WORKER_CDN;
    return mod;
  });
  return pdfjsPromise;
}
/* eslint-enable @typescript-eslint/no-explicit-any */

/** Extract token estimate from a text-based file (script-aware: ~4 chars/token
 *  Latin, ~1.6 CJK). */
export async function estimateTokensFromText(file: File): Promise<number> {
  const text = await file.text();
  return Math.max(500, estimateTokensFromString(text));
}

/** Extract token estimate from a .docx file using mammoth (script-aware). */
export async function estimateTokensFromDocx(file: File): Promise<number> {
  const mammoth = await import("mammoth");
  const arrayBuffer = await file.arrayBuffer();
  const result = await mammoth.extractRawText({ arrayBuffer });
  return Math.max(500, estimateTokensFromString(result.value));
}

/** Estimate tokens from an .epub file using file-size heuristic.
 *  EPUB is a ZIP of XHTML — assume ~10% of file size is actual text.
 *  NOTE: this byte-size heuristic is NOT script-aware (the browser doesn't unzip
 *  the XHTML), so for a CJK EPUB this web pre-flight under-counts ~2.5x vs the
 *  actual server/CLI run, which extracts text and uses script-aware estimation.
 *  EPUB papers are rare; the other formats (TXT/DOCX/PDF) are script-aware. */
export async function estimateTokensFromEpub(file: File): Promise<number> {
  const textBytes = file.size * 0.1;
  return Math.max(500, Math.round(textBytes / 4));
}

/** Extract text from a PDF and return estimated token count (script-aware:
 *  ~4 chars/token Latin, ~1.6 CJK). */
export async function estimateTokensFromPdf(file: File): Promise<number> {
  const pdfjsLib = await loadPdfJs();

  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise;

  // Concatenate the extracted text so CJK detection sees the real characters,
  // not just a character count (CJK packs ~1.6 tokens/char, not 4).
  let text = "";
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    for (const item of content.items) {
      if ("str" in item) text += item.str;
    }
  }

  return Math.max(500, estimateTokensFromString(text));
}

const TOKENS_PER_SECTION = pipelineSpec.tokensPerSection;
const MAX_REVIEWABLE_SECTIONS = pipelineSpec.maxReviewableSections;
const MIN_SECTIONS = pipelineSpec.minSections;
const SECTION_PROMPT_OVERHEAD = pipelineSpec.sectionPromptOverhead;
const OVERVIEW_INPUT_OVERHEAD = pipelineSpec.overviewInputOverhead;

const TOKENS_PER_PAGE = pipelineSpec.tokensPerPage;
const OCR_COST_PER_PAGE = pipelineSpec.ocrCostPerPage;

const MATH_SECTION_FRACTION = pipelineSpec.mathSectionFraction;
const CROSS_SECTION_MIN_SECTIONS = pipelineSpec.crossSectionMinSections;
const MAX_CROSS_SECTION_CALLS = pipelineSpec.maxCrossSectionCalls;

const AVG_COMMENTS_PER_SECTION = pipelineSpec.avgCommentsPerSection;
const TOKENS_PER_COMMENT = pipelineSpec.tokensPerComment;
const EDITORIAL_OVERHEAD = pipelineSpec.editorialOverhead;
const OVERVIEW_CONTEXT_OVERHEAD = pipelineSpec.overviewContextOverhead;
const REASONING_OVERHEAD_MULTIPLIER = pipelineSpec.reasoningOverheadMultiplier;
const FIXED_STAGE_INPUT_TOKENS = pipelineSpec.fixedStageInputTokens;

const LITERATURE_FLAT_COST = pipelineSpec.literatureFlatCost;
const DEEP_LITERATURE_FLAT_COST = pipelineSpec.deepLiteratureFlatCost;
const EXTRACTION_QA_FLAT_COST = pipelineSpec.extractionQaFlatCost;
const COST_BUFFER = pipelineSpec.costBuffer;
const STAGE_OUTPUT_TOKENS = pipelineSpec.stageOutputTokens;

const REASONING_MODEL_PREFIXES: readonly string[] = pipelineSpec.reasoningModelPrefixes;
const REASONING_MODEL_SUBSTRINGS: readonly string[] = pipelineSpec.reasoningModelSubstrings;
const NON_REASONING_SUBSTRINGS: readonly string[] = pipelineSpec.nonReasoningSubstrings;

function isReasoningModel(modelId: string): boolean {
  const lower = modelId.toLowerCase().replace(/^openrouter\//, "");
  // The `-chat` carve-out overrides the broad gpt-5 prefix below, but only for
  // the gpt-5 family — kept in lockstep with models.is_reasoning_model so it
  // can't suppress reasoning for an unrelated `-chat`-named model.
  if (lower.startsWith("openai/gpt-5") || lower.startsWith("gpt-5")) {
    for (const substr of NON_REASONING_SUBSTRINGS) {
      if (lower.includes(substr)) return false;
    }
  }
  for (const prefix of REASONING_MODEL_PREFIXES) {
    if (lower.startsWith(prefix)) return true;
  }
  for (const substr of REASONING_MODEL_SUBSTRINGS) {
    if (lower.includes(substr)) return true;
  }
  return false;
}

/** Estimate section count from token count (capped at MAX_REVIEWABLE_SECTIONS). */
function estimateSectionCount(tokenEstimate: number): number {
  return Math.max(
    MIN_SECTIONS,
    Math.min(MAX_REVIEWABLE_SECTIONS, Math.floor(tokenEstimate / TOKENS_PER_SECTION)),
  );
}

function estimateCrossSectionCount(sectionCount: number): number {
  return Math.min(MAX_CROSS_SECTION_CALLS, Math.floor(sectionCount / CROSS_SECTION_MIN_SECTIONS));
}

/**
 * Estimate total review cost in USD.
 * Mirrors build_cost_estimate() from src/coarse/cost.py. Stage list and
 * per-stage token budgets must match the Python version exactly.
 */
export function estimateReviewCost(
  tokenEstimate: number,
  pricing: ModelPricing,
  modelId: string = "",
  isPdf: boolean = true,
  sectionCount?: number,
  hasOpenRouterKey: boolean = true,
  deepLiteratureSearch: boolean = false,
): number {
  const totalTokens = Math.max(0, tokenEstimate);

  let sections = sectionCount ?? estimateSectionCount(totalTokens);
  // Guard against section_count=0 so the division below doesn't explode.
  sections = Math.max(1, sections);

  const mathSectionCount = Math.max(0, Math.round(sections * MATH_SECTION_FRACTION));
  const crossSectionCount = estimateCrossSectionCount(sections);

  const sectionTextTokens = Math.max(1, Math.floor(totalTokens / sections));
  const sectionInput = sectionTextTokens + SECTION_PROMPT_OVERHEAD;

  // Editorial reads all downstream comments + full paper markdown. Comments
  // come from section agents + completeness + proof_verify + cross_section,
  // not just section agents.
  const nEditorialComments =
    sections * AVG_COMMENTS_PER_SECTION +
    AVG_COMMENTS_PER_SECTION +
    mathSectionCount * AVG_COMMENTS_PER_SECTION +
    crossSectionCount * 2;
  const editorialIn =
    nEditorialComments * TOKENS_PER_COMMENT + EDITORIAL_OVERHEAD + totalTokens;

  // Flat-fee stages (non-LLM / non-review-model).
  const estPages = Math.max(1, Math.floor(totalTokens / TOKENS_PER_PAGE));
  let total = estPages * OCR_COST_PER_PAGE; // pdf_extraction
  if (isPdf) {
    // extraction_qa only runs on PDFs in the real pipeline (pipeline.py:226).
    total += EXTRACTION_QA_FLAT_COST;
  }

  // Default-model stages mirror pipeline.py:review_paper() 1:1.
  // Format: [name, tokens_in, tokens_out]
  const stages: [string, number, number][] = [
    ["metadata", FIXED_STAGE_INPUT_TOKENS.metadata, STAGE_OUTPUT_TOKENS.metadata],
    ["math_detection", FIXED_STAGE_INPUT_TOKENS.math_detection, STAGE_OUTPUT_TOKENS.math_detection],
    ["calibration", FIXED_STAGE_INPUT_TOKENS.calibration, STAGE_OUTPUT_TOKENS.calibration],
  ];

  if (hasOpenRouterKey) {
    total += deepLiteratureSearch ? DEEP_LITERATURE_FLAT_COST : LITERATURE_FLAT_COST;
  } else {
    stages.push(
      [
        "literature_query_gen",
        FIXED_STAGE_INPUT_TOKENS.literature_query_gen,
        STAGE_OUTPUT_TOKENS.literature_query_gen,
      ],
      [
        "literature_ranking",
        FIXED_STAGE_INPUT_TOKENS.literature_ranking,
        STAGE_OUTPUT_TOKENS.literature_ranking,
      ],
    );
  }

  stages.push(
    [
      "contribution_extraction",
      FIXED_STAGE_INPUT_TOKENS.contribution_extraction,
      STAGE_OUTPUT_TOKENS.contribution_extraction,
    ],
    ["overview", totalTokens + OVERVIEW_INPUT_OVERHEAD, STAGE_OUTPUT_TOKENS.overview],
    // Completeness reads the full paper via _build_sections_text
    // (agents/completeness.py:44), not a small 3k prompt.
    ["completeness", totalTokens + OVERVIEW_CONTEXT_OVERHEAD, STAGE_OUTPUT_TOKENS.completeness],
    // Section agents (parallel, one per reviewable section).
    ...Array.from(
      { length: sections },
      (_, i) =>
        [`section_${i + 1}`, sectionInput, STAGE_OUTPUT_TOKENS.section] as [
          string,
          number,
          number,
        ],
    ),
    // Proof verify (chained after section agents for math sections).
    ...Array.from(
      { length: mathSectionCount },
      (_, i) =>
        [
          `proof_verify_${i + 1}`,
          sectionInput + OVERVIEW_CONTEXT_OVERHEAD,
          STAGE_OUTPUT_TOKENS.proof_verify,
        ] as [string, number, number],
    ),
    // Cross-section synthesis (conditional, up to 3).
    ...Array.from(
      { length: crossSectionCount },
      (_, i) =>
        [
          `cross_section_${i + 1}`,
          sectionTextTokens * 2 + OVERVIEW_CONTEXT_OVERHEAD,
          STAGE_OUTPUT_TOKENS.cross_section,
        ] as [string, number, number],
    ),
    ["editorial", editorialIn, STAGE_OUTPUT_TOKENS.editorial],
  );

  const reasoning = isReasoningModel(modelId);
  for (const [, tokIn, tokOut] of stages) {
    let inp = pricing.promptCostPerToken;
    let out = pricing.completionCostPerToken;
    let selectedThreshold = -1;
    for (const tier of pricing.pricingTiers ?? []) {
      if (tokIn >= tier.minPromptTokens && tier.minPromptTokens > selectedThreshold) {
        selectedThreshold = tier.minPromptTokens;
        inp = tier.promptCostPerToken;
        out = tier.completionCostPerToken;
      }
    }
    const outWithOverhead = reasoning ? tokOut * (1 + REASONING_OVERHEAD_MULTIPLIER) : tokOut;
    total += inp * tokIn + out * outWithOverhead;
  }

  total *= COST_BUFFER;
  return total;
}
