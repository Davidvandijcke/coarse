/**
 * Client-side cost estimation for coarse reviews.
 *
 * Mirrors the heuristic from src/coarse/cost.py:
 *   OCR + metadata + 3 overview judges + synthesis + N sections + crossref + critique
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

/** Estimate section count from token count (~1,200 tokens per section). */
function estimateSectionCount(tokenEstimate: number): number {
  return Math.max(4, Math.min(40, Math.floor(tokenEstimate / 1200)));
}

/**
 * Estimate total review cost in USD.
 * Mirrors build_cost_estimate() from cost.py.
 */
export function estimateReviewCost(
  tokenEstimate: number,
  pricing: ModelPricing,
  sectionCount?: number,
): number {
  const { promptCostPerToken: inp, completionCostPerToken: out } = pricing;
  const sections = sectionCount ?? estimateSectionCount(tokenEstimate);
  const sectionTextTokens = Math.max(1, Math.floor(tokenEstimate / sections));
  // Each section prompt includes ~5,000 tokens of overhead:
  // system prompt (~1200) + overview context (~2500) + calibration (~500) + notation (~800)
  const sectionInput = sectionTextTokens + 5000;

  // OCR: ~$0.002/page, estimate pages from tokens
  const estPages = Math.max(1, Math.floor(tokenEstimate / 250));
  let total = estPages * 0.002;

  // Literature search: Perplexity Sonar Pro flat fee (web app always uses OpenRouter)
  total += 0.03;

  // Estimated raw comments from section agents (each produces 1-5, avg ~3)
  const nRawComments = sections * 3;

  // Crossref reads all raw comments, emits deduplicated set as JSON
  const crossrefIn = nRawComments * 350 + 3500;
  const crossrefOut = Math.floor(nRawComments * 0.6) * 600;

  // Critique reads deduped comments, emits revised set as JSON
  const nDeduped = Math.floor(nRawComments * 0.6);
  const critiqueIn = nDeduped * 350 + 3500;
  const critiqueOut = Math.floor(nDeduped * 0.9) * 600;

  // Pipeline stages: [name, tokens_in, tokens_out]
  const NUM_OVERVIEW_JUDGES = 3;
  const stages: [string, number, number][] = [
    ["metadata", 500, 100],
    ["calibration", 1000, 2000],
    // 3 overview judges each read full paper
    ...Array.from(
      { length: NUM_OVERVIEW_JUDGES },
      (_, i) => [`overview_judge_${i + 1}`, tokenEstimate, 1500] as [string, number, number],
    ),
    ["overview_synthesis", 5000, 1500],
    ...Array.from(
      { length: sections },
      (_, i) => [`section_${i + 1}`, sectionInput, 3500] as [string, number, number],
    ),
    ["crossref", crossrefIn, crossrefOut],
    ["critique", critiqueIn, critiqueOut],
  ];

  for (const [, tokIn, tokOut] of stages) {
    total += inp * tokIn + out * tokOut;
  }

  // Fixed cost for extraction QA (Gemini Flash, always enabled by modal worker)
  total += 0.02;

  // Conservative buffer — better to overestimate
  total *= 1.15;

  return total;
}
