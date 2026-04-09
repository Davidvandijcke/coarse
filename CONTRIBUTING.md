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
├── extraction.py       # PDF/TXT/MD/TeX/DOCX/HTML/EPUB -> markdown
├── extraction_qa.py    # Vision LLM spot-check of extraction quality
├── structure.py        # Markdown -> PaperStructure (sections, math detection, domain)
├── pipeline.py         # review_paper() orchestrator
├── synthesis.py        # Review -> markdown output
├── quote_verify.py     # Fuzzy-match quotes against paper text (stricter for math)
├── llm.py              # litellm wrapper, cost tracking
├── models.py           # Model ID constants (single source of truth)
├── prompts.py          # All LLM prompt templates
├── types.py            # Pydantic models
├── cost.py             # Cost estimation + user approval
├── garble.py           # OCR garble detection and normalization
├── quality.py          # Quality eval against reference review (dev only)
└── agents/
    ├── base.py             # ReviewAgent ABC + prompt caching support
    ├── overview.py         # 3-judge panel overview (macro-level feedback)
    ├── section.py          # Per-section detailed review
    ├── crossref.py         # Cross-reference deduplication
    ├── critique.py         # Self-critique quality gate
    ├── verify.py           # Adversarial proof verification for math sections
    └── literature.py       # Literature search (Perplexity Sonar Pro, arXiv fallback)
```

## How the pipeline works

```
paper.pdf (or .txt, .md, .tex, .docx, .html, .epub)
  -> extraction.py       Mistral OCR / Docling fallback -> PaperText
  -> extraction_qa.py    Vision LLM spot-check (auto-triggers on garbled text)
  -> structure.py        Parse headings + LLM classify + math detection -> PaperStructure
  -> calibrate_domain \
                       |  Parallel: domain-specific criteria + literature search
  -> search_literature /  (Perplexity Sonar Pro, arXiv fallback)
  -> overview panel       3-judge panel with different personas -> synthesized OverviewFeedback
  -> section agents   \
                       |  Parallel: detailed comments + adversarial proof verification
  -> proof verify      /  (math sections only)
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
