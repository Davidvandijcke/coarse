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

coarse uses a two-branch model:

- **`main`** — stable, tagged releases only. Protected: direct pushes are disallowed; changes land only via release PRs from `dev`. Each merge to `main` is tagged with a semantic version (`v1.1.0`, `v1.2.0`, …).
- **`dev`** — active development. All feature work targets `dev`. When `dev` has accumulated enough changes to warrant a release, open a PR from `dev` to `main`, bump the version, and tag.

```
feat/my-feature  ─►  dev  ─►  main  (release PR + tag)
```

### Branch naming

Branch off **`dev`** (not `main`) using one of:

```
feat/<description>    # New features
fix/<description>     # Bug fixes
docs/<description>    # Documentation only
chore/<description>   # Tooling, CI, dependencies
```

### Commits

Use [conventional commits](https://www.conventionalcommits.org/):

```
feat(pipeline): add parallel section processing
fix(extraction): handle scanned PDFs without text layer
docs: update changelog for v1.2.0
test(agents): add edge case for empty sections
```

Scope is optional but encouraged. Focus the subject line on the *why*, not the *what* — the diff already shows the *what*.

### Versioning

coarse follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (`2.0.0`) — breaking changes to the public API or CLI
- **MINOR** (`1.2.0`) — new features, no breaking changes
- **PATCH** (`1.1.1`) — bug fixes only

Version bumps happen **only on release PRs from `dev` to `main`**. Feature PRs into `dev` must NOT bump the version — that's the release manager's job. The version lives in two places that must stay in sync (CI enforces this):

- `pyproject.toml` → `[project] version = "..."`
- `src/coarse/__init__.py` → `__version__ = "..."`

### Pre-PR checklist

If you use Claude Code, run `/pre-pr` — it runs every check below plus the
security scanner and five parallel review agents. Otherwise, run them
manually:

- [ ] `python3 scripts/security_scanner.py` reports no CRITICAL findings (or `make security`)
- [ ] `bash scripts/doc-sync-check.sh` exits 0
- [ ] `uv run ruff check src/ tests/` passes (or `make lint`)
- [ ] `uv run pytest tests/ -v` passes (or `make test`)
- [ ] `CHANGELOG.md` updated under `## Unreleased` in the appropriate subsection (`Added` / `Changed` / `Fixed` / `Removed`)
- [ ] New code has tests in `tests/test_<module>.py`
- [ ] Commit messages follow conventional commits
- [ ] PR targets `dev` (not `main`) — unless you're the maintainer cutting a release

### Claude Code slash commands

Workflow automation lives in `.claude/commands/`. Run with a `/` in chat.

| Command | When to use it |
|---|---|
| `/pre-pr` | Before every push. Security gate + doc sync + 5 parallel review agents + lint/tests/changelog. |
| `/security-review` | Standalone security audit. Blocking gate inside `/pre-pr`; also runs in CI via `.github/workflows/security.yml`. |
| `/architecture-review` | After a big refactor or new agent. Import graph + layer check + 3 parallel structural agents. |
| `/module-review` | Focused audit of one module against the 11-point bug checklist. Supports `--module <path>`, `--changed`, `--all`. |
| `/worktree-start` | Create a new worktree off `dev` for a feature/fix. |
| `/dev-loop` | Supervised autonomous development loop for component builds. |

## Submitting a PR

1. Fork the repository (external contributors) or create a branch directly (maintainers).
2. Branch off `dev`: `git checkout dev && git pull && git checkout -b feat/my-feature`
3. Make your changes, commit with a conventional message.
4. Run `make check` (lint + tests).
5. Update `CHANGELOG.md` under `## Unreleased`.
6. Open a PR against **`dev`**.

### Cutting a release (maintainers only)

When `dev` is ready to release:

1. On `dev`, bump the version in `pyproject.toml` and `src/coarse/__init__.py`.
2. Rename the `## Unreleased` heading in `CHANGELOG.md` to `## vX.Y.Z — YYYY-MM-DD`, and add a fresh empty `## Unreleased` section above it.
3. Commit: `git commit -m "release: vX.Y.Z"`.
4. Open a PR from `dev` → `main` titled `release: vX.Y.Z`.
5. After merge, tag the merge commit on `main`: `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`.
6. Fast-forward `dev` to `main` so both branches line up for the next cycle: `git checkout dev && git merge --ff-only main && git push`.

## Reporting issues

Open an issue at [github.com/Davidvandijcke/coarse/issues](https://github.com/Davidvandijcke/coarse/issues). Include:

- coarse version (`coarse --version`)
- Python version
- OS
- Steps to reproduce
- Error output / logs

Maintainers apply `area: *` and `priority: *` labels during triage — contributors don't need to pick these. Every new issue gets a `needs triage` label automatically; once a maintainer has looked at it, that label is removed.

**Security issues**: if you find something sensitive (exposed secrets, auth bypass, etc.), please email david.van.dijcke@gmail.com instead of opening a public issue. Use the `security` label for non-sensitive security-related improvements.
