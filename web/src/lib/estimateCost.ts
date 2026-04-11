/**
 * Client-side cost estimation for coarse reviews.
 *
 * Mirrors the heuristic from src/coarse/cost.py 1:1. When the Python
 * estimator changes, this file must change with it. Both list the same
 * stages with the same per-stage token budgets and the same _COST_BUFFER.
 *
 * Token estimate: extract text via pdf.js (loaded from CDN to avoid webpack issues).
 * Pricing: fetched from OpenRouter /api/v1/models.
 */

const PDFJS_CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.9.155/pdf.min.mjs";
const PDFJS_WORKER_CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.9.155/pdf.worker.min.mjs";

/** Per-token pricing (USD) from OpenRouter /api/v1/models */
export interface ModelPricing {
  promptCostPerToken: number;
  completionCostPerToken: number;
}

let pricingCache: Map<string, ModelPricing> | null = null;

/** Fetch and cache the full OpenRouter pricing map. */
async function fetchPricingMap(): Promise<Map<string, ModelPricing>> {
  if (pricingCache) return pricingCache;
  const resp = await fetch("https://openrouter.ai/api/v1/models");
  const data = await resp.json();
  const map = new Map<string, ModelPricing>();
  for (const m of data.data ?? []) {
    if (m.id && m.pricing?.prompt) {
      map.set(m.id, {
        promptCostPerToken: parseFloat(m.pricing.prompt),
        completionCostPerToken: parseFloat(m.pricing.completion ?? "0"),
      });
    }
  }
  pricingCache = map;
  return map;
}

export async function getModelPricing(modelId: string): Promise<ModelPricing | null> {
  const map = await fetchPricingMap();
  return map.get(modelId) ?? null;
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

/** Extract token estimate from a text-based file (~4 chars/token). */
export async function estimateTokensFromText(file: File): Promise<number> {
  const text = await file.text();
  return Math.max(500, Math.round(text.length / 4));
}

/** Extract token estimate from a .docx file using mammoth (~4 chars/token). */
export async function estimateTokensFromDocx(file: File): Promise<number> {
  const mammoth = await import("mammoth");
  const arrayBuffer = await file.arrayBuffer();
  const result = await mammoth.extractRawText({ arrayBuffer });
  return Math.max(500, Math.round(result.value.length / 4));
}

/** Estimate tokens from an .epub file using file-size heuristic.
 *  EPUB is a ZIP of XHTML — assume ~10% of file size is actual text. */
export async function estimateTokensFromEpub(file: File): Promise<number> {
  const textBytes = file.size * 0.1;
  return Math.max(500, Math.round(textBytes / 4));
}

/** Extract text from a PDF and return estimated token count (~4 chars/token). */
export async function estimateTokensFromPdf(file: File): Promise<number> {
  const pdfjsLib = await loadPdfJs();

  const arrayBuffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) }).promise;

  let totalChars = 0;
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    for (const item of content.items) {
      if ("str" in item) totalChars += item.str.length;
    }
  }

  // ~4 chars per token for English academic text
  return Math.max(500, Math.round(totalChars / 4));
}

// Heuristic constants — mirror src/coarse/cost.py (verified 2026-04-11).
// When a Python constant changes, update it here too.
const TOKENS_PER_SECTION = 1200;
const MAX_REVIEWABLE_SECTIONS = 25; // mirrors pipeline.py's reviewable_sections[:25]
const MIN_SECTIONS = 4;
const SECTION_PROMPT_OVERHEAD = 8000;

const TOKENS_PER_PAGE = 250;
const OCR_COST_PER_PAGE = 0.002;

const MATH_SECTION_FRACTION = 0.2;
const CROSS_SECTION_MIN_SECTIONS = 6;
const EXPECTED_CROSS_SECTION_CALLS = 1;

const AVG_COMMENTS_PER_SECTION = 3;
const TOKENS_PER_COMMENT = 350;
const EDITORIAL_OVERHEAD = 5000;
const OVERVIEW_CONTEXT_OVERHEAD = 5000;

const LITERATURE_FLAT_COST = 0.03;
// Gemini Flash extraction QA on a typical paper (~45k in + 4096 out at
// $0.50/$3.00 per 1M) runs about $0.035. Approximate as a flat fee rather
// than fetching vision model pricing separately.
const EXTRACTION_QA_FLAT_COST = 0.035;

const COST_BUFFER = 1.3;

// Reasoning model detection — mirrors `is_reasoning_model` in
// src/coarse/models.py. Uses both prefix and substring rules so
// thinking/reasoning variants across providers all get the 4x overhead
// applied to tokens_out. Keep in sync with REASONING_MODEL_PREFIXES and
// REASONING_MODEL_SUBSTRINGS in models.py.
const REASONING_MODEL_PREFIXES: readonly string[] = [
  "openai/o1",
  "openai/o3",
  "openai/o4",
  "openai/gpt-5-pro",
  "openai/gpt-5.1-pro",
  "openai/gpt-5.2-pro",
  "openai/gpt-5.3-pro",
  "openai/gpt-5.4-pro",
  "deepseek/deepseek-r",
  "x-ai/grok-4",
  "x-ai/grok-3-mini",
  "perplexity/sonar-reasoning",
  "arcee-ai/maestro-reasoning",
];
const REASONING_MODEL_SUBSTRINGS: readonly string[] = [
  "thinking",
  "reasoning",
  "deep-research",
];
// Empirical: reasoning models bill ~4x the visible output budget in hidden
// reasoning tokens, charged at the output-token rate. See
// _REASONING_OVERHEAD_MULTIPLIER in src/coarse/llm.py.
const REASONING_OVERHEAD_MULTIPLIER = 4;

function isReasoningModel(modelId: string): boolean {
  const lower = modelId.toLowerCase().replace(/^openrouter\//, "");
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
): number {
  const { promptCostPerToken: inp, completionCostPerToken: out } = pricing;
  const totalTokens = Math.max(0, tokenEstimate);

  let sections = sectionCount ?? estimateSectionCount(totalTokens);
  // Guard against section_count=0 so the division below doesn't explode.
  sections = Math.max(1, sections);

  const mathSectionCount = Math.max(0, Math.round(sections * MATH_SECTION_FRACTION));
  const crossSectionCount =
    sections >= CROSS_SECTION_MIN_SECTIONS ? EXPECTED_CROSS_SECTION_CALLS : 0;

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
  total += LITERATURE_FLAT_COST; // literature_search (OpenRouter flat fee)
  if (isPdf) {
    // extraction_qa only runs on PDFs in the real pipeline (pipeline.py:226).
    total += EXTRACTION_QA_FLAT_COST;
  }

  // Default-model stages mirror pipeline.py:review_paper() 1:1.
  // Format: [name, tokens_in, tokens_out]
  const stages: [string, number, number][] = [
    ["metadata", 500, 256],
    ["math_detection", 2000, 1024],
    ["calibration", 1500, 2048],
    ["contribution_extraction", 3000, 2048],
    // Overview is a SINGLE agent call at max_tokens=8192 (no 3-judge panel;
    // see agents/overview.py:80).
    ["overview", totalTokens + 3000, 8192],
    // Completeness reads the full paper via _build_sections_text
    // (agents/completeness.py:44), not a small 3k prompt.
    ["completeness", totalTokens + OVERVIEW_CONTEXT_OVERHEAD, 4096],
    // Section agents (parallel, one per reviewable section).
    ...Array.from(
      { length: sections },
      (_, i) => [`section_${i + 1}`, sectionInput, 10000] as [string, number, number],
    ),
    // Proof verify (chained after section agents for math sections).
    ...Array.from(
      { length: mathSectionCount },
      (_, i) =>
        [
          `proof_verify_${i + 1}`,
          sectionInput + OVERVIEW_CONTEXT_OVERHEAD,
          16384,
        ] as [string, number, number],
    ),
    // Cross-section synthesis (conditional, up to 3).
    ...Array.from(
      { length: crossSectionCount },
      (_, i) =>
        [
          `cross_section_${i + 1}`,
          sectionTextTokens * 2 + OVERVIEW_CONTEXT_OVERHEAD,
          8192,
        ] as [string, number, number],
    ),
    // Editorial pass (replaces legacy crossref+critique).
    ["editorial", editorialIn, 24000],
  ];

  const reasoning = isReasoningModel(modelId);
  for (const [, tokIn, tokOut] of stages) {
    const outWithOverhead = reasoning ? tokOut * (1 + REASONING_OVERHEAD_MULTIPLIER) : tokOut;
    total += inp * tokIn + out * outWithOverhead;
  }

  total *= COST_BUFFER;
  return total;
}
