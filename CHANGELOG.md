# Changelog

## [Unreleased]

### Added

- **Model manifest** (`models.py`) — Single source of truth for all model IDs, replacing scattered constants in cli.py, config.py, llm.py.
- **Quote verification** (`quote_verify.py`) — Post-processing fuzzy match of comment quotes against paper text; drops or flags unverifiable quotes.
- **Post-extraction QA** (`extraction_qa.py`) — Vision LLM spot-checks Docling output against page images for papers with figures/tables.
- **CI pipeline** (`.github/workflows/ci.yml`) — Ruff lint (advisory), pytest (blocking), version consistency check on every PR.
- **Pre-PR command** (`.claude/commands/pre-pr.md`) — 5-agent parallel code review integrated into push workflow.
- **Evaluation data** (`data/refine_examples/`) — Reference reviews and papers for quality scoring.
- **New tests** — `test_quote_verify.py`, `test_domain_calibration.py`, `test_multi_judge.py`, `test_section_routing.py`.

### Changed

- **Replace PDF pipeline with Docling** — Single-pass document conversion replaces the 3-source pymupdf4llm/fitz/vision-LLM stack. Section text is now a substring of full_markdown, fixing quote verification mismatches. Structure extraction via markdown heading parsing instead of vision-LLM (~$0.05-0.10/paper → free). Scanned PDFs now supported via Docling OCR.

### Removed

- **Vision-based structure extraction** — Removed `--vision` CLI flag and vision-LLM structure extraction pipeline. `vision_model` config field kept for post-extraction QA. Page rendering repurposed for QA spot-checks.
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
- **Synthesis** (`synthesis.py`): Deterministically renders a `Review` object to the refine.ink
  markdown format.
- **LLM layer** (`llm.py`): litellm wrapper with instructor for structured Pydantic output; tracks
  per-call cost.
- **Cost estimation** (`cost.py`): Pre-flight cost estimate with a configurable spending cap and
  interactive user approval gate.
- **Config management** (`config.py`): Reads and writes `~/.coarse/config.toml`; resolves API
  keys from environment variables or the config file.
- **CLI** (`cli.py`): `coarse setup` for interactive configuration; `coarse review paper.pdf` for
  reviewing a paper; `--model`, `--output`, `--vision`, and `--yes` flags.
- **Quality eval** (`quality.py`): Developer-only tool that scores a generated review against a
  reference review using an LLM judge.
- **Type definitions** (`types.py`): All shared Pydantic models (`PaperText`, `PaperStructure`,
  `Review`, `DetailedComment`, `CostEstimate`, etc.).
- **Prompt templates** (`prompts.py`): All LLM prompt templates in one place.
