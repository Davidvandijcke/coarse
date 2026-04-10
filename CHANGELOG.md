# Changelog

## Unreleased

### Added

- **Web: Log in with OpenRouter** — the submission form now has a "Log in with OpenRouter" button that runs OpenRouter's browser-only OAuth PKCE flow and fills in the API key automatically. The returned key is stored in the browser's localStorage so users stay logged in across visits; a "Log out" control clears it. The manual paste field is kept as a fallback for users who prefer to use a scoped key. The server contract is unchanged — the key is still only sent in the `/api/submit` body when a review is submitted and never persisted server-side. Closes #12.

### Changed

- **Mistral OCR is now OpenRouter-only** — removed the `_extract_mistral_direct` backend that tried to hit Mistral's API directly with a `MISTRAL_API_KEY`. All PDF OCR now routes through OpenRouter's `file-parser` plugin, so users only ever need an `OPENROUTER_API_KEY`. The OCR → Docling fallback chain is unchanged for offline use.
- **Raised Modal concurrency from 10 → 20 containers**, removed the web-side hard rejection gate so bursts beyond the container limit are queued by Modal instead of erroring out.
- **OpenRouter OCR retry budget raised from 3 to 5 attempts.** Total exponential backoff window is now 1s + 2s + 4s + 8s + 16s = 31s, giving more headroom for slow recovery on the file-parser plugin.
- **Modal function memory raised from 2 GB to 4 GB.** Large PDFs (8+ MB) plus the Docling torch/RapidOCR stack can exceed 2 GB when OCR falls through to offline mode. 4 GB keeps the offline fallback usable for big documents.
- **PDFs are no longer deleted from Supabase Storage on the `finally` path** of the Modal worker. They're only deleted on the success path now; failed reviews keep their PDF so Modal's infrastructure retries (or a manual resubmit of the same job_id) can actually find it. Stale PDFs from failed runs are swept by the daily cleanup cron at 24h.

### Fixed

- **Docling fallback works in production** — added `libgl1` + `libglib2.0-0` to the Modal image. Without them, Docling crashed on first import with `libGL.so.1: cannot open shared object file`, meaning the "offline fallback" wasn't actually a fallback when the OpenRouter OCR path failed.
- **OpenRouter OCR error handling** — when OpenRouter returns HTTP 200 with an error body (rate limit, plugin unavailable, content policy), extraction no longer crashes with `KeyError: 'choices'`. Instead it raises a clean `ExtractionError` with the provider's error message, which the orchestrator can then classify into a user-facing message. Also handles missing `choices`, malformed annotations, empty content, and non-dict JSON responses.
- **OpenRouter OCR retry logic** — added bounded retries (3 → 5 attempts, exponential backoff 1s/2s/4s/8s/16s) on connection errors, read timeouts, and transient HTTP statuses (408, 429, 500, 502, 503, 504). Non-transient 4xx errors (401 bad key, 402 spend limit) fail fast without wasting retries. Diagnostic logging on every retry and every unexpected response shape.
- **Retry OpenRouter OCR when the error is wrapped in a 200 response body.** The file-parser plugin occasionally returns `HTTP 200` with `{"error": {"code": 504, "message": "Timed out parsing ..."}}` instead of a raw `504`. The previous retry logic only matched on transport status codes, so it treated these as immediate failures. Now retries whenever the body's `error.code` is in the same retryable set (408, 429, 500, 502, 503, 504).
- **Modal-level retries work again.** Previously, if Modal infrastructure retried a review (after an OOM or container crash), the retry would 404 on the PDF because the `finally` block had already deleted it from Supabase Storage. See the PDF storage change above.

## v1.1.0 — 2026-04-10

### Added

- **Multi-format support** — `extract_file()` router supports .txt, .md, .tex, .latex, .html, .docx, and .epub in addition to PDF. Quality-first strategy: Docling (if installed) for .docx/.html/.tex, with lightweight fallbacks (mammoth, markdownify, regex). PDFs always use Mistral OCR first. New optional dependency group: `pip install coarse[formats]` for .docx/.html/.epub fallback support; .txt/.md/.tex require no extra dependencies.
- **No-retention provider routing** — All OpenRouter-routed requests now include `provider.data_collection: "deny"`, instructing OpenRouter to route only to model providers that do not retain or train on user data. No-op for direct Anthropic/OpenAI/Google API calls.

### Changed

- **Literature search: Perplexity Sonar Pro** — Primary literature search now uses `perplexity/sonar-pro-search` via OpenRouter for web-grounded results with real citations (~12s, ~$0.03). Returns both related work and open questions/known limitations. arXiv pipeline kept as automatic fallback when OPENROUTER_API_KEY is unavailable or Perplexity fails.

### Fixed

- **OpenRouter auth: pass `api_key` explicitly** — `_inject_openrouter_privacy()` now also injects `OPENROUTER_API_KEY` from env into the litellm call kwargs for `openrouter/*` models. Fixes a production failure on Modal where reviews aborted with `401 "Missing Authentication header"` despite the env var being set at the moment of the check. Relying on litellm's implicit env-var lookup was flaky; passing the key directly is deterministic.

## v1.0.0 — 2026-03-09

First public release.

### Added

- **Web hosting infrastructure** — Vercel (Next.js) + Supabase (auth/DB/storage) + Modal (serverless compute) architecture for hosted web version. Two tiers: free (data-sharing consent for research) and BYOK (user's own OpenRouter key).
- **Mistral OCR extraction** — Primary PDF extraction uses Mistral OCR via litellm (94% math accuracy). Docling kept as offline fallback. Priority: MISTRAL_API_KEY direct → OpenRouter file-parser plugin → Docling.
- **Post-extraction QA** (`extraction_qa.py`) — Vision LLM spot-checks extraction output against page images for papers with figures/tables.
- **Model manifest** (`models.py`) — Single source of truth for all model IDs.
- **Quote verification** (`quote_verify.py`) — Post-processing fuzzy match of comment quotes against paper text; drops or flags unverifiable quotes.
- **Domain calibration** — Generates domain-specific review criteria from paper content.
- **Literature search** — arXiv-based literature context for review agents.
- **CI pipeline** (`.github/workflows/ci.yml`) — Ruff lint (advisory), pytest (blocking), version consistency check on every PR.
- **Evaluation data** (`data/refine_examples/`) — Reference reviews and papers for quality scoring.

### Changed

- **Anthropic prompt caching** — Overview panel judges share cached paper context via `cache_control`, reducing input token costs ~90% on cache hits. Judges run sequentially for Anthropic models to ensure cache sharing. Section/crossref/critique agents also annotate system prompts for caching.
- **Structured assumption cross-check** — 4-step procedure for cross-checking theoretical assumptions against empirical methodology.
- **Appendix proof coverage** — Appendix sections classified as "proof" are now reviewed instead of skipped.
- **Anti-redundancy prompts** — Section agents instructed not to restate overview issues; crossref dedup removes comments that duplicate overview issues.
- **Anti-truncation quote instructions** — Strict "NEVER truncate mid-equation" rule in all section prompts.
- **Quote verify expansion** — `_trim_to_best_match` uses a 1.5x window to expand truncated quotes instead of re-truncating correct matches.
- **Optional heavy dependencies** — `docling` moved to optional extra (`pip install coarse[docling]`). Core install is lightweight.

### Fixed

- **LaTeX garbling in review quotes** — Added `verify_quotes` call after critique agent (which re-garbles LaTeX via JSON round-trip). Added LaTeX preservation instructions to all section prompts.

### Removed

- **Agentic mode** — Removed `--agentic` CLI flag, coding agents, and `openai-agents` dependency. Standard LLM agents provide comparable quality with simpler architecture.
- **Vision-based structure extraction** — Removed `--vision` CLI flag. Structure extraction via markdown heading parsing instead.
- **pymupdf4llm dependency** — Replaced by `docling>=2.0`. pymupdf kept for extraction QA page rendering.

## v0.1.0 — 2026-03-03

Initial release.

### Features

- **PDF extraction** (`extraction.py`): Convert PDF papers to text using pymupdf4llm; optional
  vision mode for scanned or image-heavy PDFs.
- **Structure analysis** (`structure.py`): LLM-based parsing of paper into title, domain,
  taxonomy, abstract, and labelled sections with claims and definitions.
- **Overview agent** (`agents/overview.py`): Produces 4-6 macro-level issues covering the paper
  as a whole (runs in parallel with section agents).
- **Section agents** (`agents/section.py`): One agent per section produces 15-25 detailed
  comments with verbatim quotes from the paper.
- **Cross-reference agent** (`agents/crossref.py`): Deduplicates comments, validates quotes, and
  checks consistency across agents.
- **Critique agent** (`agents/critique.py`): Self-critiques the draft review and revises weak
  comments as a quality gate.
- **Pipeline** (`pipeline.py`): Orchestrates extraction, structure analysis, all agents, and
  synthesis into a single `review_paper()` call.
- **Synthesis** (`synthesis.py`): Deterministically renders a `Review` object to structured
  markdown format.
- **LLM layer** (`llm.py`): litellm wrapper with instructor for structured Pydantic output; tracks
  per-call cost.
- **Cost estimation** (`cost.py`): Pre-flight cost estimate with a configurable spending cap and
  interactive user approval gate.
- **Config management** (`config.py`): Reads and writes `~/.coarse/config.toml`; resolves API
  keys from environment variables or the config file.
- **CLI** (`cli.py`): `coarse setup` for interactive configuration; `coarse review paper.pdf` for
  reviewing a paper; `--model`, `--output`, and `--yes` flags.
- **Quality eval** (`quality.py`): Developer-only tool that scores a generated review against a
  reference review using an LLM judge.
- **Type definitions** (`types.py`): All shared Pydantic models (`PaperText`, `PaperStructure`,
  `Review`, `DetailedComment`, `CostEstimate`, etc.).
- **Prompt templates** (`prompts.py`): All LLM prompt templates in one place.
