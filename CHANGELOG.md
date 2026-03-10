# Changelog

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
