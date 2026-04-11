# Changelog

## Unreleased

### Changed

- **Landing-page model picker refreshed** — `web/src/components/ModelPicker.tsx` now defaults to `anthropic/claude-opus-4.6` as the pre-selected model and adds `openai/gpt-5.4` and `google/gemini-3.1-pro-preview` as featured options. `qwen/qwen3.5-plus-02-15` was bumped to `qwen/qwen3.6-plus` to reflect the new release on OpenRouter. All four IDs were verified against OpenRouter's live catalog before landing.

### Fixed

- **Null-byte crashes on Supabase write** — `_sanitized_completion` in `src/coarse/llm.py` stripped literal control characters (`\x00-\x1f`) from raw LLM response text but did not touch the JSON escape sequence `\u0000` (six printable ASCII bytes). When an LLM emitted `\u0000` inside a JSON string field, the escape survived the sanitizer, `json.loads` reconstituted it as a real `\x00` inside the parsed Pydantic field, and the resulting `result_markdown` then crashed the Supabase UPDATE with Postgres 22P05 (`\u0000 cannot be converted to text`), marking the review as failed despite the pipeline having succeeded. Observed in production during the post-launch tweet surge on two gpt-5.4 reviews (`6c41a05e`, `92947b4b`) — extraction produced clean markdown on both PDFs, so the null byte could only have entered through the LLM response path. Fix strips the `\\u0000` escape form before Instructor/Pydantic parses the content. Regression covered by three new tests in `tests/test_llm.py` exercising `_sanitized_completion` directly.

## v1.1.3 — 2026-04-11

First release under the new `coarse-ink` PyPI name. `uvx coarse-ink review paper.pdf ...` now works end-to-end. The PyPI version history for `coarse-ink` skips 1.1.1 and 1.1.2 — 1.1.0 was published manually from an earlier branch while the rename was still in draft, and this release catches up to the in-repo version. Also ships new incident monitoring and structured error classification for backend observability.

### Fixed

- **PyPI distribution renamed to `coarse-ink`** — the bare `coarse` name on PyPI was already taken by an unrelated, abandoned package (`coarse==0.0.1` by a different author), so `uvx coarse` / `pip install coarse` resolved to the wrong package and users hit `Package 'coarse' does not provide any executables` (#17). Installing is now `uvx coarse-ink review paper.pdf ...` or `pip install coarse-ink`. The Python import name (`import coarse`) and the `coarse` CLI command are unchanged — a `coarse-ink` console script is also registered so `uvx coarse-ink ...` resolves directly, and `uv tool install coarse-ink` still puts a `coarse` command on your PATH.

### Added

- **Automated incident posting to X/Twitter** — new `deploy/incident_monitor.py` Modal app (`coarse-monitor`) that runs every 2 minutes, watches four independent signals (backend error spike, queue stall, Modal `/health` down, upstream provider 5xx pattern), and posts an "investigating" tweet when the backend is actually broken. Auto-resolves (threaded reply) once signals have been clear for 10 minutes. Explicitly ignores user-side errors (bad API keys, spending limits, 429s from the user's own provider) so it never tweets because someone pasted a dead key. Ships in `INCIDENT_MONITOR_MODE=dry_run` by default; flip to `live` via Modal secret once dry-run logs look right. Includes 30 min cooldown between incidents to suppress flapping and an `INCIDENT_MONITOR_ENABLED=false` kill switch.
- **Structured error classification on failed reviews** — new `reviews.error_category` column distinguishes `user_auth` / `user_quota` / `user_forbidden` / `user_rate_limit` from `provider_5xx` / `extraction` / `backend_timeout` / `backend_unknown`. Classifier lives in `deploy/error_classify.py` so the incident monitor can query it without re-parsing unstructured `error_message` strings. Requires `deploy/migrate_incidents.sql` to be applied to Supabase.

## v1.1.2 — 2026-04-11

Internal tooling release. No user-facing changes to the `coarse` package on
PyPI — this release ships dev-workflow automation (security scanner, slash
commands, pre-commit hooks, CI gates) plus a small refactor that re-aligns
`src/coarse/llm.py` with the "model IDs live in `models.py` only" rule.

### Fixed

- **`llm.py` no longer hardcodes model IDs** — the `_CUSTOM_MODEL_INFO` dict keyed on literal `"qwen/qwen3.5-plus-02-15"` and `"moonshotai/kimi-k2.5"` now imports `DEFAULT_MODEL` and the new `KIMI_K2_5_MODEL` constant from `coarse.models`, restoring the "model IDs live in `models.py` only" invariant from CLAUDE.md. The security scanner's `hardcoded-model-id` check was also extended to cover `moonshotai`, `kimi`, `groq`, `together`, `xai`, and `cohere` provider prefixes so future drift gets caught.

### Added

- **Security scanner + `/security-review` command** — new zero-dep `scripts/security_scanner.py` (stdlib only) scans the repo for known leaked secret fingerprints (stored as SHA-256 hashes, never plaintext), provider-key patterns (OpenAI / Anthropic / Google / OpenRouter / Perplexity / Supabase / Stripe / GitHub / AWS / private keys / URL-embedded creds), insecure `.env` permissions, and model-ID string literals outside `src/coarse/models.py`. Skips docstrings via AST and supports inline `# security: ignore` suppression. Backed by 14 tests in `tests/test_security.py` (synthetic fingerprint via monkeypatch — no real key material in the test fixtures). Runs in CI (`.github/workflows/security.yml --strict`), from `make security`, and from the `/security-review` slash command which adds 3 parallel in-session agents for API-key lifecycle, HTTP surface, and prompt-injection audits.
- **`/architecture-review` command** — lightweight macro-level structural review with inline AST-based import-graph analysis (cycles, layer violations, oversized files, fan-in leaders) plus 3 parallel in-session agents for coupling, data flow, and simplification.
- **`/module-review` command** — focused per-module audit against coarse's 11-point bug checklist (model-IDs-only-in-models.py, LLMClient wrapper, instructor/Pydantic, prompts centralization, no-print, test coverage, context managers, cost tracking, resolve_api_key, extraction robustness, quote verification). Supports `--module`, `--changed`, `--all`, `--review-only`.
- **`scripts/doc-sync-check.sh`** — lightweight bash sync check used by `/pre-pr`: verifies every `src/coarse/*.py` is listed in CLAUDE.md, CHANGELOG has an `## Unreleased` section, `pyproject.toml` version matches `src/coarse/__init__.py`, and no new model-ID literals slipped into the diff outside `models.py`.
- **Pre-commit hooks** — `.pre-commit-config.yaml` wires ruff, ruff-format, trailing-whitespace, end-of-file-fixer, check-yaml/toml, large-file guard, private-key detector, merge-conflict check, plus the local security scanner. Install with `make install-hooks`.
- **CI security workflow** — `.github/workflows/security.yml` runs the scanner in `--strict` mode on every push and PR to `main`/`dev`, plus advisory `pip-audit`.
- **CLAUDE.md: Worktree Discipline + Parallel Development sections** documenting the `/private/tmp/coarse-<slug>/` pattern, full-path rule for Edit/Write, and the 4-concurrent-worktree cap for parallel Claude Code sessions.
- **CLAUDE.md: Slash Commands section** listing every command and its purpose.
- **Makefile targets**: `make security`, `make install-hooks`.

### Changed

- **`/pre-pr` upgraded** — new Step 0 is a BLOCKING security gate via `security_scanner.py` (CRITICAL halts, `--strict` also halts on HIGH); new Step 1.5 runs `doc-sync-check.sh`; git diff base fixed from `main...HEAD` to `dev...HEAD` (feature PRs target `dev` per CONTRIBUTING.md); added a 6th review agent that re-runs the scanner against the diff and checks new code for `os.getenv("*_API_KEY")` bypasses, missing HTTP timeouts, and prompt-injection-unsafe templates.
- **`/worktree-start` bases worktrees off `dev`** (was `main`). Worktree slug format now `coarse-<issue>-<slug>`. Reminder output mentions the shell-cwd-resets-between-Bash-calls trap and the `gh pr create --base dev` convention.
- **CLAUDE.md package structure** — added the 5 agents that had drifted off the tree (`completeness.py`, `cross_section.py`, `editorial.py`, `contradiction.py`, plus top-level `recall.py`). Marks `crossref.py`, `contradiction.py`, `critique.py` as legacy (superseded by `editorial.py`).
- **Stripped 10 cached curl commands** containing inline Supabase/OpenRouter secrets from `.claude/settings.local.json` (local-only file, never tracked in git, `.gitignore` already covers `.claude/`). Tightened `.env` and `web/.env.local` permissions from 0o644 → 0o600.

## v1.1.1 — 2026-04-10

### Added

- **Web: Log in with OpenRouter** — the submission form now has a "Log in with OpenRouter" button that runs OpenRouter's browser-only OAuth PKCE flow and fills in the API key automatically. The returned key is stored in the browser's localStorage so users stay logged in across visits; a "Log out" control clears it. The manual paste field is kept as a fallback for users who prefer to use a scoped key. The server contract is unchanged — the key is still only sent in the `/api/submit` body when a review is submitted and never persisted server-side. Closes #12.

### Changed

- **Mistral OCR is now OpenRouter-only** — removed the `_extract_mistral_direct` backend that tried to hit Mistral's API directly with a `MISTRAL_API_KEY`. All PDF OCR now routes through OpenRouter's `file-parser` plugin, so users only ever need an `OPENROUTER_API_KEY`. The OCR → Docling fallback chain is unchanged for offline use.
- **Raised Modal concurrency from 10 → 20 containers**, removed the web-side hard rejection gate so bursts beyond the container limit are queued by Modal instead of erroring out.
- **OpenRouter OCR retry budget raised from 5 to 10 attempts** with a 32s per-retry backoff cap. Sequence is now 1s + 2s + 4s + 8s + 16s + 32s × 4 = 159s max, giving much more headroom for Mistral OCR's upstream timeouts while keeping the total wait bounded. A new cost guard inspects the `usage` field of every 200-with-error-body response and refuses to retry if the request was actually billed, so the retry bump can't multiply the user's API cost.
- **PDF extraction chain now has three tiers: Mistral OCR → pdf-text (OpenRouter) → Docling.** The new middle tier uses OpenRouter's free `pdf-text` file-parser engine, which extracts embedded PDF text without involving Mistral OCR at all. It catches Mistral OCR upstream outages (persistent 504 timeouts) without paying Docling's torch/RapidOCR startup cost, and falls through to Docling for scanned image-only PDFs.
- **Modal function memory raised from 2 GB to 4 GB.** Large PDFs (8+ MB) plus the Docling torch/RapidOCR stack can exceed 2 GB when OCR falls through to offline mode. 4 GB keeps the offline fallback usable for big documents.
- **PDFs are no longer deleted from Supabase Storage on the `finally` path** of the Modal worker. They're only deleted on the success path now; failed reviews keep their PDF so Modal's infrastructure retries (or a manual resubmit of the same job_id) can actually find it. Stale PDFs from failed runs are swept by the daily cleanup cron at 24h.

### Fixed

- **Docling fallback works in production** — added `libgl1` + `libglib2.0-0` to the Modal image. Without them, Docling crashed on first import with `libGL.so.1: cannot open shared object file`, meaning the "offline fallback" wasn't actually a fallback when the OpenRouter OCR path failed.
- **OpenRouter OCR error handling** — when OpenRouter returns HTTP 200 with an error body (rate limit, plugin unavailable, content policy), extraction no longer crashes with `KeyError: 'choices'`. Instead it raises a clean `ExtractionError` with the provider's error message, which the orchestrator can then classify into a user-facing message. Also handles missing `choices`, malformed annotations, empty content, and non-dict JSON responses.
- **OpenRouter OCR retry logic** — added bounded retries (3 → 5 attempts, exponential backoff 1s/2s/4s/8s/16s) on connection errors, read timeouts, and transient HTTP statuses (408, 429, 500, 502, 503, 504). Non-transient 4xx errors (401 bad key, 402 spend limit) fail fast without wasting retries. Diagnostic logging on every retry and every unexpected response shape.
- **Retry OpenRouter OCR when the error is wrapped in a 200 response body.** The file-parser plugin occasionally returns `HTTP 200` with `{"error": {"code": 504, "message": "Timed out parsing ..."}}` instead of a raw `504`. The previous retry logic only matched on transport status codes, so it treated these as immediate failures. Now retries whenever the body's `error.code` is in the same retryable set (408, 429, 500, 502, 503, 504).
- **Modal-level retries work again.** Previously, if Modal infrastructure retried a review (after an OOM or container crash), the retry would 404 on the PDF because the `finally` block had already deleted it from Supabase Storage. See the PDF storage change above.
- **Extraction QA no longer logs spurious "Page N out of range" warnings.** When Mistral OCR emitted more `<!-- PAGE BREAK -->` markers than the PDF had pages (trailing empty chunks, or a page split mid-content), `_select_qa_pages` could propose a page number that fitz rejected. Now clamps scored page numbers and the final selection set to `num_pages`.
- **Math section detection logs the underlying exception** instead of a bare "failed" message, so transient LLM errors are actually diagnosable from the Modal worker logs.
- **Math section detection no longer silently fails for Claude-family models.** The LLM call passed `max_tokens=256`, which was fine for Qwen/DeepSeek but too tight for Claude 4-family models (Opus, Sonnet) that sometimes write a prose preamble before emitting the tool call. At 256 the preamble alone could hit `finish_reason='length'` and instructor raised `InstructorRetryException("The output is incomplete due to a max_tokens length limit.")` before any JSON was produced, forcing the keyword-heuristic fallback. Bumped to 1024 and tightened `MATH_DETECTION_SYSTEM` to tell the model to skip the preamble and emit the structured response directly. Diagnosed from real user review `1e786d50`.

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
