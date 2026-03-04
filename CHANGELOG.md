# Changelog

## [Unreleased]

### Added

- **Coding agents** (`coding_agent.py`, `agents/coding_section.py`, `agents/coding_critique.py`) — OpenHands SDK integration for autonomous paper analysis. Coding agents can read full paper text, cross-reference sections, and run Python to verify math. Opt-in via `--agentic` CLI flag with transparent fallback to standard LLM agents on failure.
- **CodingReviewAgent ABC** (`agents/base.py`) — Abstract base class for file-workspace-based coding agents with `prepare_workspace()` and `output_schema()`.
- **`--agentic` CLI flag** — Enables coding agents for proof/methodology/results sections and critique pass (~$2-3 extra, 3-10 min vs ~30s).
- **Coding agent config** — `use_coding_agents`, `agent_model`, `agent_budget_usd`, `max_coding_sections` on `CoarseConfig`.
- **AGENT_MODEL constant** (`models.py`) — `moonshotai/kimi-k2.5` for coding agent LLM.
- **Coding agent tests** — `test_coding_agent.py` (12 tests), `test_coding_section.py` (10 tests), `test_coding_critique.py` (10 tests).
- **Model manifest** (`models.py`) — Single source of truth for all model IDs, replacing scattered constants in cli.py, config.py, llm.py.
- **Quote verification** (`quote_verify.py`) — Post-processing fuzzy match of comment quotes against paper text; drops or flags unverifiable quotes.
- **Post-extraction QA** (`extraction_qa.py`) — Vision LLM spot-checks Docling output against page images for papers with figures/tables.
- **CI pipeline** (`.github/workflows/ci.yml`) — Ruff lint (advisory), pytest (blocking), version consistency check on every PR.
- **Pre-PR command** (`.claude/commands/pre-pr.md`) — 5-agent parallel code review integrated into push workflow.
- **Evaluation data** (`data/refine_examples/`) — Reference reviews and papers for quality scoring.
- **New tests** — `test_quote_verify.py`, `test_domain_calibration.py`, `test_multi_judge.py`, `test_section_routing.py`.

### Changed

- **Python 3.12+ required** — Upgraded from 3.11+ to support `openhands-sdk` dependency.
- **`openhands-sdk` is a core dependency** — Moved from optional to required for coding agent support.
- **Pipeline hybrid dispatch** — `review_paper()` routes proof/methodology/results sections to coding agents when `--agentic` enabled, capped at `max_coding_sections` (default 3). Other sections use standard LLM agents.
- **Cost estimation** — Pre-flight estimate includes coding agent costs (~$0.50/section + $1.00/critique) when agentic mode enabled.
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
