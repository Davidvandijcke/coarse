# Contributing to coarse

Contributions are welcome! coarse is a free, open-source AI academic paper reviewer and we appreciate bug reports, feature requests, and code contributions.

## Development setup

Requirements: Python 3.12+, [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/Davidvandijcke/coarse.git
cd coarse
uv sync --extra dev
uv run pytest tests/ -v      # run tests
uv run ruff check src/ tests/ # lint
```

Or use `make`:

```bash
make check   # lint + test
make test    # tests only
make lint    # lint only
make format  # auto-format
```

## Project structure

```
src/coarse/
├── cli.py              # Typer CLI, progress display
├── config.py           # ~/.coarse/config.toml, API key management
├── extraction.py       # PDF -> markdown (Mistral OCR, Docling fallback)
├── extraction_qa.py    # Vision LLM spot-check of extraction quality
├── structure.py        # Markdown -> PaperStructure (sections, domain)
├── pipeline.py         # review_paper() orchestrator
├── synthesis.py        # Review -> markdown output
├── quote_verify.py     # Fuzzy-match quotes against paper text
├── llm.py              # litellm wrapper, cost tracking
├── models.py           # Model ID constants (single source of truth)
├── prompts.py          # All LLM prompt templates
├── types.py            # Pydantic models
├── cost.py             # Cost estimation + user approval
├── coding_agent.py     # OpenAI Agents SDK wrapper
├── garble.py           # OCR garble detection and normalization
└── agents/
    ├── base.py             # ReviewAgent + CodingReviewAgent ABCs
    ├── overview.py         # Macro-level feedback (4-6 issues)
    ├── section.py          # Per-section detailed review
    ├── coding_section.py   # Deep section review (coding agents)
    ├── crossref.py         # Cross-reference deduplication
    ├── critique.py         # Self-critique quality gate
    ├── coding_critique.py  # Deep critique (coding agents)
    └── literature.py       # arXiv literature search
```

## How the pipeline works

```
paper.pdf
  -> extraction.py       Mistral OCR / Docling fallback -> PaperText
  -> extraction_qa.py    Vision LLM spot-check (optional)
  -> structure.py        Parse headings + LLM classify -> PaperStructure
  -> overview agent  \
                      |  Run in parallel
  -> section agents  /
  -> crossref agent      Deduplicate, validate quotes, consistency
  -> quote_verify.py     Programmatic fuzzy-match quotes against text
  -> critique agent      Self-critique quality gate, revise weak comments
  -> quote_verify.py     Re-verify (critique can re-garble quotes via JSON)
  -> synthesis.py        Deterministic render -> paper_review.md
```

## Development rules

1. **Simplicity first.** Minimum code that solves the problem. No speculative features or abstractions for single-use code.
2. **Every file gets tests.** Tests go in `tests/test_{module}.py`.
3. **Prompts in `prompts.py`.** All LLM prompt templates in one file.
4. **Models in `models.py`.** Never hardcode model ID strings outside this file.
5. **Types in `types.py`.** All Pydantic models for the pipeline.
6. **Structured output.** Use `instructor` + Pydantic for all LLM responses.
7. **Use `uv run`** for all commands (pytest, ruff, python).

## Git workflow

### Branch naming

```
feat/<description>    # New features
fix/<description>     # Bug fixes
docs/<description>    # Documentation only
```

### Commits

Use [conventional commits](https://www.conventionalcommits.org/):

```
feat(pipeline): add parallel section processing
fix(extraction): handle scanned PDFs without text layer
docs: update changelog for v0.1.1
test(agents): add edge case for empty sections
```

### Pre-PR checklist

- [ ] `uv run ruff check src/ tests/` passes
- [ ] `uv run pytest tests/ -v` passes
- [ ] `CHANGELOG.md` updated with your change
- [ ] Version bumped in `pyproject.toml` and `src/coarse/__init__.py` (if releasing)

## Submitting a PR

1. Fork the repository
2. Create a branch (`feat/my-feature`)
3. Make your changes
4. Run `make check` (or lint + test manually)
5. Update `CHANGELOG.md`
6. Open a PR against `main`

## Reporting issues

Open an issue at [github.com/Davidvandijcke/coarse/issues](https://github.com/Davidvandijcke/coarse/issues). Include:

- coarse version (`coarse --version`)
- Python version
- OS
- Steps to reproduce
- Error output / logs
