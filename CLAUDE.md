# CLAUDE.md — coarse

## What This Is

Free, open-source AI academic paper reviewer. The rough alternative to refine.ink.
Users provide their own API keys and pay only the LLM provider directly (~$2-5 per review vs refine.ink's ~$50).

**Package:** `coarse` (Python 3.11+, Pydantic, litellm, instructor)
**Install:** `pip install coarse` / `pipx install coarse` / `uvx coarse paper.pdf`

## Python Environment

Use `uv run` for all commands:
```bash
uv run pytest tests/ -v
uv run python -m coarse paper.pdf
```

## Architecture

### Review Pipeline

```
paper.pdf
    → [extraction.py]   Docling → PaperText (single high-quality markdown)
    → [extraction_qa.py] Vision LLM spot-check (skipped for clean text papers)
    → [structure.py]     Parse headings + cheap LLM → PaperStructure (sections, domain)
    → [overview agent]   LLM → 4-6 macro issues (parallel with section agents)
    → [section agents]   LLM → 15-25 detailed comments (1 per section, parallel)
    → [crossref agent]   LLM → deduplicate, validate quotes, consistency
    → [critique agent]   LLM → self-critique quality gate, revise weak comments
    → [synthesis.py]     Deterministic → paper_review.md (refine.ink format)
```

### Package Structure

```
src/coarse/
├── __init__.py              # __version__, review_paper()
├── __main__.py              # python -m coarse
├── cli.py                   # Typer CLI, progress display (rich)
├── config.py                # ~/.coarse/config.toml, API key management
├── cost.py                  # Cost estimation + user approval gate
├── extraction.py            # PDF → PaperText (Docling markdown)
├── extraction_qa.py         # Post-extraction QA via vision LLM (Gemini Flash)
├── structure.py             # PaperText → PaperStructure (heading parse + LLM metadata)
├── quote_verify.py          # Post-processing quote verification
├── models.py                # Model manifest — single source of truth for all model IDs
├── llm.py                   # litellm wrapper, model registry, cost tracking
├── prompts.py               # All prompt templates
├── types.py                 # Pydantic models
├── pipeline.py              # review_paper() orchestrator
├── synthesis.py             # Review → markdown string
├── quality.py               # Quality eval against reference (dev only)
└── agents/
    ├── __init__.py
    ├── base.py              # ReviewAgent ABC
    ├── overview.py          # Macro-level feedback (4-6 issues)
    ├── section.py           # Per-section detailed review
    ├── crossref.py          # Cross-reference consistency
    └── critique.py          # Self-critique quality gate
```

### Key Types (types.py)

- `PaperText` — extracted PDF content (full_markdown, token_estimate)
- `PaperStructure` — title, domain, taxonomy, abstract, sections[]
- `SectionInfo` — number, title, text, section_type, claims[], definitions[]
- `PaperMetadata` — domain, taxonomy (response model for LLM classification)
- `OverviewFeedback` — issues[] (4-6 macro issues with title + body)
- `DetailedComment` — number, title, status, quote (verbatim), feedback
- `Review` — complete output (overall_feedback + detailed_comments)
- `CostEstimate` / `CostStage` — pre-flight cost breakdown

### LLM Layer (llm.py)

Uses `litellm` for unified provider interface + `instructor` for structured Pydantic output.
`LLMClient` wraps both, tracks cost per call.
Auto-detects API keys from env vars or `~/.coarse/config.toml`.

### Dependencies

Core: litellm, instructor, docling, pydantic, typer, rich, tomli-w, pymupdf
Dev: pytest, ruff

## Reference Review

The gold standard is `data/refine_examples/r3d/feedback-regression-discontinuity-design-with-distribution--2026-03-03.md`.
Study its format: metadata block → Overall Feedback (4-6 titled issues) → Detailed Comments (20 numbered, each with quote + feedback).

## Output Format

Must match refine.ink format exactly:
```markdown
# Paper Title

**Date**: MM/DD/YYYY
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

Here are some overall reactions to the document.

**Issue Title**

Issue body paragraph...

**Status**: [Pending]

---

## Detailed Comments (N)

### 1. Comment title

**Status**: [Pending]

**Quote**:
> Exact verbatim text from the paper

**Feedback**:
Explanation of issue + constructive remediation guidance.

---
```

## Git Workflow

### Branch Naming

```
feat/<issue>-<description>    # New features
fix/<issue>-<description>     # Bug fixes
docs/<description>            # Documentation only
```

### Conventional Commits

```
feat(pipeline): add parallel section processing
fix(extraction): handle scanned PDFs without text layer
docs: update changelog for v0.1.1
test(agents): add edge case for empty sections
refactor(llm): simplify cost tracking
```

### Before Every Commit

1. `uv run ruff check src/ tests/` — fix lint errors
2. `uv run pytest tests/ -v` — all tests pass
3. Verify version consistency: `pyproject.toml` matches `src/coarse/__init__.py`

### Pre-PR Checklist

1. **CHANGELOG.md** — Add entry for the change. Every PR, no exceptions.
2. **Tests** — New functionality has tests. Existing tests pass.
3. **Lint** — `ruff check` passes.
4. **Version** — Bump in both `pyproject.toml` and `__init__.py` if releasing.

### CI Pipeline (.github/workflows/ci.yml)

Runs on every push to main and every PR:
- **Ruff lint** — advisory (non-blocking)
- **pytest** — blocking
- **Version consistency** — blocking (pyproject.toml must match __init__.py)

## Development Rules

1. **Simplicity first.** Minimum code that solves the problem.
2. **Every file gets tests.** Tests go in `tests/test_{module}.py`.
3. **Use `uv run pytest tests/ -v`** to verify before committing.
4. **Match existing patterns.** Look at what's already built before writing new code.
5. **Don't over-engineer.** No abstractions for single-use code. No speculative features.
6. **Prompts in prompts.py.** All LLM prompt templates go in one file, not scattered.
7. **Structured output.** Use instructor + Pydantic models for all LLM responses.

## Model Preferences

- **Default model**: `qwen/qwen3.5-plus-02-15` (via OpenRouter)
- **Vision model**: `gemini/gemini-3-flash` — used for post-extraction QA (spot-checks Docling output against page images). Skipped automatically for clean text-only papers.
- Structure extraction uses heading parsing from Docling markdown + cheap text-LLM metadata call.
- All model IDs are defined in `models.py`. `config.py` imports defaults from there. Don't hardcode model strings elsewhere.

## What NOT to Do

- Don't commit `.env`, API keys, `.DS_Store`, `__pycache__/`
- Don't add dependencies without checking pyproject.toml first
- Don't create config systems beyond `~/.coarse/config.toml`
- Don't hardcode model names outside models.py
