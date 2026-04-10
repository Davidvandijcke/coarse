# CLAUDE.md — coarse

## What This Is

Free, open-source AI academic paper reviewer. The rough alternative to refine.ink.
Users provide their own API keys and pay only the LLM provider directly (~$2-5 per review vs refine.ink's ~$50).

**Package:** `coarse` (Python 3.12+, Pydantic, litellm, instructor)
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
paper (PDF, TXT, MD, TeX, DOCX, HTML, EPUB)
    → [extraction.py]    Mistral OCR (OpenRouter) → pdf-text (OpenRouter) → Docling → PaperText (markdown)
    → [extraction_qa.py] Vision LLM spot-check (auto-triggers on garbled text)
    → [structure.py]     Parse headings + LLM → PaperStructure (sections, math detection, domain)
    → [calibrate_domain] Domain-specific review criteria (parallel with literature)
    → [literature.py]    Perplexity Sonar Pro search, arXiv fallback (parallel with calibration)
    → [overview panel]   3-judge panel → synthesized OverviewFeedback (4-6 macro issues)
    → [section agents]   LLM → 15-25 detailed comments (1 per section, parallel)
    → [verify agent]     Adversarial proof verification (math sections only, chained)
    → [crossref agent]   LLM → deduplicate, validate quotes, consistency
    → [quote_verify.py]  Programmatic → fuzzy-match quotes (stricter for math)
    → [critique agent]   LLM → self-critique quality gate, revise weak comments
    → [quote_verify.py]  Programmatic → re-verify quotes (critique re-garbles via JSON)
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
├── extraction.py            # PDF/TXT/MD/TeX/DOCX/HTML/EPUB → PaperText
├── extraction_qa.py         # Post-extraction QA via vision LLM (Gemini Flash)
├── structure.py             # PaperText → PaperStructure (heading parse + math detection + LLM metadata)
├── quote_verify.py          # Post-processing quote verification (stricter for math)
├── models.py                # Model manifest — single source of truth for all model IDs
├── garble.py                # OCR garble detection and normalization
├── llm.py                   # litellm wrapper, model registry, cost tracking
├── prompts.py               # All prompt templates
├── types.py                 # Pydantic models
├── pipeline.py              # review_paper() orchestrator
├── synthesis.py             # Review → markdown string
├── quality.py               # Quality eval against reference (dev only)
└── agents/
    ├── __init__.py
    ├── base.py              # ReviewAgent ABC + _build_messages helper + prompt caching
    ├── overview.py          # 3-judge panel overview (macro-level feedback, 4-6 issues)
    ├── section.py           # Per-section detailed review
    ├── crossref.py          # Cross-reference consistency
    ├── critique.py          # Self-critique quality gate
    ├── verify.py            # Adversarial proof verification (math sections)
    └── literature.py        # Literature search (Perplexity Sonar Pro, arXiv fallback)
```

### Key Types (types.py)

- `PaperText` — extracted document content (full_markdown, token_estimate, garble_ratio)
- `PaperStructure` — title, domain, taxonomy, abstract, sections[]
- `SectionInfo` — number, title, text, section_type, math_content, claims[], definitions[]
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

Core: litellm, instructor, pydantic, typer, rich, tomli-w, pymupdf, python-dotenv
Optional: docling (PDF/DOCX/HTML/TeX fallback), mammoth/markdownify/ebooklib (format fallbacks)
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

**See `CONTRIBUTING.md` for the full workflow.** Short version:

- **`main`** — stable, tagged releases only. Protected: changes land via release PR from `dev`.
- **`dev`** — active development. Feature work branches off `dev` and PRs back into `dev`.
- **Release cycle**: `feat/my-thing` → PR into `dev` → merge → periodically PR `dev` → `main` + version bump + tag.
- **Commits**: conventional commits (`feat(scope):`, `fix(scope):`, `docs:`, `test(scope):`, `chore(scope):`).
- **Pre-PR**: `make check` (ruff + pytest), update `CHANGELOG.md` under `## Unreleased`, new code has tests in `tests/test_{module}.py`. Version bumps happen only on release PRs from `dev` to `main`, not on feature PRs.

CI (`.github/workflows/ci.yml`) runs on every push to `main` or `dev` and on every PR. Pytest and version consistency (pyproject.toml must match `src/coarse/__init__.py`) are blocking; ruff lint is advisory.

## Development Rules

1. **Simplicity first.** Minimum code that solves the problem.
2. **Every file gets tests.** Tests go in `tests/test_{module}.py`.
3. **Use `uv run pytest tests/ -v`** to verify before committing.
4. **Match existing patterns.** Look at what's already built before writing new code.
5. **Don't over-engineer.** No abstractions for single-use code. No speculative features.
6. **Prompts in prompts.py.** All LLM prompt templates go in one file, not scattered.
7. **Structured output.** Use instructor + Pydantic models for all LLM responses.

## Model Manifest (models.py)

**`src/coarse/models.py` is the single source of truth for ALL model IDs.** Never hardcode model strings in any other file — always `from coarse.models import DEFAULT_MODEL, VISION_MODEL, CHEAP_MODELS`.

Current models (verified 2026-04-10):
- **Default**: `qwen/qwen3.5-plus-02-15` (via OpenRouter, 1M ctx, $0.26/1.56 per 1M tok)
- **Vision**: `gemini/gemini-3-flash-preview` (1M ctx, $0.50/3.00 per 1M tok) — post-extraction QA (litellm uses `gemini/` prefix)
- **OCR**: Mistral OCR, always routed through OpenRouter's `file-parser` plugin (never direct). Required: only `OPENROUTER_API_KEY`.
- **OpenRouter Extraction**: `google/gemini-3-flash-preview` — the host model that carries the file-parser plugin request
- **Literature Search**: `perplexity/sonar-pro-search` — web-grounded literature search via OpenRouter (~$0.03)
- **Quality Eval**: `gemini/gemini-3-flash-preview` — dev-only quality evaluation (single-judge or panel)
- **Cheap (OpenAI)**: `openai/gpt-5.1-codex-mini` ($0.25/2.00)
- **Cheap (Anthropic)**: `anthropic/claude-haiku-4.5` ($1.00/5.00)
**Hard rules:**
- NEVER write a model ID string literal outside `models.py`. Import the constant.
- Tests that reference models must `from coarse.models import ...`, not hardcode strings.
- Before changing model IDs, verify on OpenRouter: `python3 ~/.claude/skills/latest-models/scripts/fetch_models.py --search=<model>`
- Model IDs go stale fast. The `gemini/` prefix is wrong for OpenRouter (use `google/`). Old IDs like `gpt-4o-mini`, `claude-3-5-haiku-20241022` are deprecated.

## What NOT to Do

- Don't commit `.env`, API keys, `.DS_Store`, `__pycache__/`
- Don't add dependencies without checking pyproject.toml first
- Don't create config systems beyond `~/.coarse/config.toml`
- Don't hardcode model names outside models.py
