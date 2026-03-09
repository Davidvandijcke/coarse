/**
 * Client-side cost estimation for coarse reviews.
 *
 * Mirrors the heuristic from src/coarse/cost.py:
 *   OCR + metadata + overview + N sections + crossref + critique
 *
 * Token estimate: extract text via pdf.js (loaded from CDN to avoid webpack issues).
 * Pricing: fetched from OpenRouter /api/v1/models.
 */

const DEFAULT_SECTION_COUNT = 8;
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

/**
 * Estimate total review cost in USD.
 * Mirrors build_cost_estimate() from cost.py.
 */
export function estimateReviewCost(
  tokenEstimate: number,
  pricing: ModelPricing,
  sectionCount: number = DEFAULT_SECTION_COUNT,
): number {
  const { promptCostPerToken: inp, completionCostPerToken: out } = pricing;
  const sectionTokens = Math.max(1, Math.floor(tokenEstimate / sectionCount));

  // OCR: ~$0.002/page, estimate pages from tokens
  const estPages = Math.max(1, Math.floor(tokenEstimate / 250));
  let total = estPages * 0.002;

  // Pipeline stages: [name, tokens_in, tokens_out]
  const stages: [string, number, number][] = [
    ["metadata", 500, 100],
    ["overview", tokenEstimate, 1200],
    ...Array.from({ length: sectionCount }, (_, i) => [`section_${i + 1}`, sectionTokens, 600] as [string, number, number]),
    ["crossref", tokenEstimate, 1000],
    ["critique", tokenEstimate, 800],
  ];

  for (const [, tokIn, tokOut] of stages) {
    total += inp * tokIn + out * tokOut;
  }

  return total;
}
