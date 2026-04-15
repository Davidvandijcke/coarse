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
}

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
const EXTRACTION_QA_FLAT_COST = pipelineSpec.extractionQaFlatCost;
const COST_BUFFER = pipelineSpec.costBuffer;
const STAGE_OUTPUT_TOKENS = pipelineSpec.stageOutputTokens;

const REASONING_MODEL_PREFIXES: readonly string[] = pipelineSpec.reasoningModelPrefixes;
const REASONING_MODEL_SUBSTRINGS: readonly string[] = pipelineSpec.reasoningModelSubstrings;

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
): number {
  const { promptCostPerToken: inp, completionCostPerToken: out } = pricing;
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
    total += LITERATURE_FLAT_COST;
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
    const outWithOverhead = reasoning ? tokOut * (1 + REASONING_OVERHEAD_MULTIPLIER) : tokOut;
    total += inp * tokIn + out * outWithOverhead;
  }

  total *= COST_BUFFER;
  return total;
}
