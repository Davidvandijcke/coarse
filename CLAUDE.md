# CLAUDE.md — coarse

## What This Is

Free, open-source AI academic paper reviewer. The rough alternative to refine.ink.
Users provide their own API keys and pay only the LLM provider directly (~$2-5 per review vs refine.ink's ~$50).

**Package:** `coarse-ink` on PyPI; import name is still `coarse` (Python 3.12+, Pydantic, litellm, instructor). The bare `coarse` name on PyPI is held by an unrelated package — see CHANGELOG Unreleased / #17.
**Install:** `pip install coarse-ink` / `pipx install coarse-ink` / `uvx coarse-ink review paper.pdf`

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
    → [overview.py]      Single overview agent → OverviewFeedback (macro issues)
    → [completeness.py]  Structural-gap pass merged into overview
    → [section agents]   LLM → 15-25 detailed comments (1 per section, parallel)
    → [verify agent]     Adversarial proof verification (math sections only, chained)
    → [cross_section.py] Results ↔ discussion synthesis (conditional)
    → [editorial.py]     Primary filtering pass → dedup, contradiction, quality, ordering
    → [crossref.py]      Legacy fallback if editorial fails
    → [critique.py]      Legacy fallback if editorial fails
    → [quote_verify.py]  Programmatic → exact/normalized/table-aware quote verification
    → [quote_repair.py]  LLM → batched near-miss quote-anchor repair (bounded contexts only)
    → [quote_verify.py]  Programmatic → re-verify repaired quotes before synthesis
    → [synthesis.py]     Deterministic → paper_review.md (refine.ink format)
```

### Package Structure

```
src/coarse/
├── __init__.py              # __version__, review_paper()
├── __main__.py              # python -m coarse
├── cli.py                   # Typer CLI, progress display (rich)
├── cli_attach.py            # --attach signal-driven wait mode (pidfile + log tail + heartbeat watcher)
├── cli_review.py            # Standalone coarse-review CLI for headless local/handoff runs
├── claude_code_client.py    # Back-compat re-export for headless Claude client helpers
├── config.py                # ~/.coarse/config.toml, API key management
├── cost.py                  # Cost estimation + user approval gate
├── pipeline_spec.py         # Shared stage manifest for runtime + cost estimators
├── extraction.py            # PDF/TXT/MD/TeX/DOCX/HTML/EPUB → PaperText
├── extraction_cache.py      # Extraction cache paths and cache read/write helpers
├── extraction_formats.py    # Non-OpenRouter format-specific extraction backends
├── extraction_openrouter.py # OpenRouter OCR/file-parser transport and response parsing
├── extraction_qa.py         # Post-extraction QA via vision LLM (Gemini Flash)
├── headless_clients.py      # Claude/Codex/Gemini CLI-backed LLMClient replacements
├── headless_review.py       # Shared entrypoint for headless CLI review runs
├── structure.py             # PaperText → PaperStructure (heading parse + math detection + LLM metadata)
├── quote_verify.py          # Post-processing quote verification (stricter for math)
├── models.py                # Model manifest — single source of truth for all model IDs
├── garble.py                # OCR garble detection and normalization
├── llm.py                   # litellm wrapper, model registry, cost tracking
├── prompts.py               # All prompt templates
├── types.py                 # Pydantic models
├── pipeline.py              # review_paper() orchestrator
├── review_stages.py         # Stage-local review helpers used by pipeline.py
├── synthesis.py             # Review → markdown string
├── quality.py               # Quality eval against reference (dev only)
├── recall.py                # Recall eval vs. ground-truth expert reviews (dev only)
└── agents/
    ├── __init__.py
    ├── base.py              # ReviewAgent ABC + _build_messages helper + prompt caching
    ├── overview.py          # Single-pass macro-level overview feedback
    ├── section.py           # Per-section detailed review
    ├── completeness.py      # Flags structural gaps and missing content
    ├── cross_section.py     # Cross-section synthesis: discussion claims vs formal results
    ├── editorial.py         # Merged filtering pass (dedup, contradiction, quality, ordering)
    ├── crossref.py          # Cross-reference consistency (legacy, superseded by editorial)
    ├── contradiction.py     # Flags comments contradicting the paper's contribution (legacy)
    ├── critique.py          # Self-critique quality gate (legacy, superseded by editorial)
    ├── quote_repair.py      # Batched near-miss quote re-anchoring before deterministic re-check
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

### PyPI publishing is tag-driven, NOT main-merge-driven

`coarse-ink` is **not** auto-published when `dev` merges into `main`. The `.github/workflows/release.yml` workflow only fires on `push: tags: v*`, and the build job hard-fails unless the tag matches both `pyproject.toml` `version` and `src/coarse/__init__.py` `__version__`. So substantial changes can sit on `main` indefinitely without ever shipping to PyPI.

When a release PR `dev` → `main` lands, the release steps are:

1. **Inside the release PR**, bump the version in both files and move CHANGELOG entries from `## Unreleased` to `## vX.Y.Z — YYYY-MM-DD`:
   - `pyproject.toml` → `version = "X.Y.Z"`
   - `src/coarse/__init__.py` → `__version__ = "X.Y.Z"`
2. Merge the PR to `main`.
3. Tag and push from `main`:
   ```bash
   git checkout main && git pull
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
4. The `Release` workflow runs: tests → version-consistency check → `uv build` → PyPI Trusted Publishing (no API token, OIDC via the `pypi` GitHub environment).

Skipping step 3 leaves PyPI stale no matter how much code lands on `main`. Doing step 3 without step 1 fails the version-consistency check by design — that's the guardrail against accidentally tagging a mismatched release.

**Changes outside `src/coarse/`** (web, deploy, .github/workflows, data, output) ship through their own paths and do **not** require a PyPI release. Don't cut a new tag for web-only or deploy-only work; check `git diff vX.Y.Z..main -- src/coarse/` first to see if the package itself actually changed.

## Default Deploy Workflow

For any substantial deploy-affecting change, the default path is:

1. Feature branch into `dev`
2. Preview validation on isolated infra
3. Release PR `dev` -> `main`
4. Production deploy from `main`

Concretely:

- Vercel creates preview deployments for non-`main` pushes.
- `.github/workflows/modal-preview-deploy.yml` deploys both Modal apps
  from `dev` into the Modal `preview` environment when the change
  touches deploy-relevant paths; otherwise rerun it manually on `dev`
  if you need a fresh preview Modal deploy.
- Preview Vercel env vars point at preview Supabase plus preview Modal
  URLs (`MODAL_FUNCTION_URL` and `MODAL_EXTRACT_URL`), as documented in
  `deploy/PREVIEW_ENVIRONMENTS.md`.
- `.github/workflows/modal-deploy.yml` deploys both Modal apps from
  `main` to production.

Hard deploy rules:

- Big changes must soak on preview first. This includes schema
  migrations, worker changes, web API route changes, auth/env changes,
  and changes under `src/coarse/`, `deploy/`, or `web/src/app/api/`.
- Do not validate deploy-affecting changes locally against production
  Supabase when preview exists.
- Do not manually deploy production Modal from a non-`main` branch.
- Preview is not green unless both `/api/submit` and `/api/mcp-extract`
  route to preview Modal, not production.
- This is a required human release workflow, not a fully repo-enforced
  gate. The smoke test and backend-isolation check still need to be
  performed by the operator.

## Development Rules

1. **Simplicity first.** Minimum code that solves the problem.
2. **Every file gets tests.** Tests go in `tests/test_{module}.py`.
3. **Use `uv run pytest tests/ -v`** to verify before committing.
4. **Match existing patterns.** Look at what's already built before writing new code.
5. **Don't over-engineer.** No abstractions for single-use code. No speculative features.
6. **Prompts in prompts.py.** All LLM prompt templates go in one file, not scattered.
7. **Structured output.** Use instructor + Pydantic models for all LLM responses.

## Slash Commands

Workflow automation commands live in `.claude/commands/`. Invoke with a `/`
in chat.

| Command | Purpose |
|---|---|
| `/security-review` | Fingerprint + pattern scan, env perms, key lifecycle audit, HTTP surface audit, prompt-injection check. Runs `scripts/security_scanner.py` + 3 parallel in-session agents. Blocking in `/pre-pr` Step 0. |
| `/architecture-review` | Static import-graph scan (cycles, layer violations, oversized files) + 3 parallel agents (coupling, data flow, simplification). Escalates structural changes to user. |
| `/module-review` | Focused per-module audit against the 11-point bug checklist. Supports `--module <path>`, `--changed`, `--all`, `--review-only`. |
| `/pre-pr` | Blocking checklist before every push: security gate → diff capture → doc-sync → 5 parallel review agents → lint → tests → version → changelog → PR. |
| `/dev-loop` | Supervised autonomous development loop (existing). |
| `/worktree-start` | Create a worktree off `dev` for a new feature/fix (existing). |

`scripts/security_scanner.py` is standalone — it runs in CI
(`.github/workflows/security.yml`) and from `make security` without needing
a Claude Code session.

## Worktree Discipline

Parallel work happens in ephemeral git worktrees under `/private/tmp/coarse-<slug>/`.
The main repo stays on `dev` (or `main` for release branches) and is used
only for read-only exploration.

**Hard rules:**

1. **Never edit files directly in the main worktree** during a feature task.
   Use `/worktree-start` first, then all edits go through the full worktree path.
2. **Full paths on every Edit/Write.** `/private/tmp/coarse-<slug>/src/coarse/foo.py`,
   not `src/coarse/foo.py`. The shell cwd resets between `Bash` calls — `cd` alone
   doesn't persist, so relative paths break silently.
3. **Prefix every file-modifying `Bash` command** with
   `cd /private/tmp/coarse-<slug> &&`.
4. **Always `uv sync --extra dev`** in the new worktree before running tests or
   scripts — bare `uv sync` misses the dev extras.
5. **Merging back**: create PR from the worktree (`gh pr create --base dev`), merge
   via `gh pr merge --squash`, then `git -C <main-repo> pull origin dev`, then
   `git worktree remove /private/tmp/coarse-<slug>`.

## Parallel Development

coarse supports multiple concurrent Claude Code sessions as long as each
session operates in its own worktree.

- **Cap: 4 concurrent worktrees.** Beyond that, merge conflicts start to bite.
- **Every branch references a GitHub issue.** `/worktree-start <issue-number>`.
- **Worktree slug format:** `/private/tmp/coarse-<issue-number>-<short-slug>`.
- **No two worktrees touch the same file** without coordinating through the
  user — the autopilot doesn't resolve three-way merges.
- **Cross-worktree state lives only in the repo** (git branches, PRs, issues).
  Don't rely on `~/.coarse/` or any local path for cross-session coordination.

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
