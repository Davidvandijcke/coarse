# Security Review for coarse

Run a structured security review of the repo. Combines a fast static scanner
(runs in ~1 second, zero deps) with 3 parallel in-session agents that audit
key handling, HTTP surface, and prompt injection risks.

coarse handles user-provided API keys and ingests untrusted PDFs, so the goal
is narrow and concrete: **no secret ever leaves the allowed env files, no
untrusted PDF content ever reaches an instruction channel, and no dependency
ships with a known CVE we could have caught.**

## Arguments

`$ARGUMENTS` is passed through. Examples:
- `/security-review` — full review (static + 3 LLM agents), ~$1.50
- `/security-review --fast` — static scanner only, zero LLM cost
- `/security-review --scope secrets,perms` — restrict the static scan
- `/security-review --strict` — escalate HIGH findings to blocking

## Process

### Step 1: Static scan (always runs)

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && python3 scripts/security_scanner.py $ARGUMENTS
```

Record every finding. `CRITICAL` = leaked fingerprint found outside `.env`.
`HIGH` = provider-key pattern, insecure env perms, or model-ID literal in
`src/coarse/` outside `models.py`. `MEDIUM` = provider-hint false-positive
zone.

**Halt if any CRITICAL is present.** Do not proceed to Step 2. Report the
finding, tell the user which file + line, and propose the exact fix (usually
`chmod 600 <file>` or stripping the line + rotating the key).

### Step 2: Dependency audit (fast mode skips this)

```bash
cd "/Users/davidvandijcke/University of Michigan Dropbox/David Van Dijcke/coarse" && uv run --with pip-audit pip-audit --strict 2>&1 | tail -40
```

`pip-audit` is run via `uv run --with` so it doesn't have to be a permanent
dev dependency. Report any vulnerabilities at HIGH or CRITICAL CVSS.

### Step 3: Launch 3 parallel LLM agents (skip if `--fast`)

Launch **all three in one message** using the Agent tool (subagent_type:
general-purpose). Pass each the paths listed below so they don't have to
search. Budget each agent ~$0.50.

**Agent 1 — API key lifecycle audit**

Read `src/coarse/config.py`, `src/coarse/llm.py`, `src/coarse/cli.py`,
`src/coarse/extraction.py`, `deploy/modal_worker.py`, and any file under
`web/api/`. For every path that touches an API key, verify:

1. The key is never passed to `logger.{debug,info,warning,error,exception}`.
2. The key is never included in `repr()` / `str()` / f-strings that feed into
   an exception raised from that function.
3. The key is never written to a cache file (`.extraction_cache.json`,
   `~/.coarse/config.toml`) unless that file has 0o600 enforced at write time.
4. 401/403 response handling strips the `Authorization` header before logging
   or re-raising.
5. `resolve_api_key` is the only entry point for key lookup (no direct
   `os.getenv("…_API_KEY")` bypasses).

Output: `file.py:line  [OK|VIOLATION] <description>` per checkpoint, then a
summary of any violations ranked CRITICAL / HIGH / MEDIUM.

**Agent 2 — HTTP surface audit**

Grep the codebase (`src/`, `deploy/`, `web/`) for every outbound HTTP call:
`requests.`, `httpx.`, `litellm.completion`, `fetch(`, `axios.`, `urllib`,
`urlopen`. For each call site, verify:

1. The URL is HTTPS (or an explicit localhost for dev).
2. No API key is embedded in the URL path or query string.
3. `verify=False` / `rejectUnauthorized: false` is NOT set.
4. A timeout is set (or the caller has a documented justification for blocking
   indefinitely).
5. Error paths do not echo request headers back to the user.

Output: ranked violations with `file:line` references.

**Agent 3 — Prompt injection audit**

coarse pipes untrusted PDF content into LLM prompts. Read
`src/coarse/prompts.py` and every agent under `src/coarse/agents/`. For each
prompt template, verify:

1. System-prompt text and user content live in separate `messages` entries
   (not concatenated into one string).
2. Untrusted content is fenced with clear delimiters (e.g., XML tags like
   `<paper_text>…</paper_text>`) so the model can ignore instructions inside.
3. No prompt takes user content and interpolates it into a `do this: {content}`
   format where the content could be interpreted as a directive.
4. Tool use is either disabled for untrusted-content steps or the tool surface
   is reviewed (only the scanner's `extraction_qa` uses vision — confirm it
   cannot be coerced into executing user-supplied instructions).

Output: for each prompt template, `template_name  [SAFE|UNSAFE] <reason>`.

### Step 4: Aggregate + decide

Collect findings from all three agents plus the static scanner. Classify each
as:

| Severity | Examples |
|---|---|
| **CRITICAL** | Leaked fingerprint in tracked file, key printed in logger, `verify=False` on a production call, raw user content in a system prompt |
| **HIGH** | Provider-key pattern match outside env files, missing timeout on litellm call, untrusted content without delimiter fencing, known-CVE dependency at CVSS ≥ 7 |
| **MEDIUM** | Pre-existing model-ID hardcode, permissive-but-not-leaking cache write, stale error message that echoes part of an API response |
| **LOW** | Style / hardening recommendations |

**Always escalate to the user:**
- Any CRITICAL finding — do not auto-fix; present the plan and wait for approval.
- Any HIGH finding that would require modifying `src/coarse/llm.py` or `src/coarse/config.py` (these are load-bearing).
- Any finding in `deploy/` (production path).

**May auto-fix without asking:**
- Stripping a newly-added secret from an unpushed commit.
- Adding a `# security: ignore` marker on a line the agent confirmed is a true false positive.
- Running `chmod 600` on a local env file.
- Adding a missing timeout to a non-production `httpx.get` call.

### Step 5: Report

Output a single summary block:

```
Security review: <branch>
  Static:       <N> findings (CRITICAL=<a> HIGH=<b> MEDIUM=<c>)
  Dependencies: <N> vulnerable packages (fast: skipped)
  Key lifecycle:   <N> violations
  HTTP surface:    <N> violations
  Prompt injection: <N> violations

  Auto-fixed: <N> (list with file:line)
  Requires review: <N> (list with file:line and proposed change)
```

If `/security-review` was invoked as a step from `/pre-pr`, return a terse
pass/fail signal: `security: OK` or `security: BLOCKED — <one-line reason>`.

## Important notes

- The static scanner has **zero** external deps. If `pip-audit` is missing,
  Step 2 prints a warning and continues.
- The fingerprint list in `scripts/security_scanner.py::LEAKED_FINGERPRINTS`
  is the source of truth. Add a new fingerprint every time a key is scrubbed
  from the repo.
- Suppress a true false-positive on a single line with a trailing
  `# security: ignore` comment (works in `.py`, `.sh`, `.ts`, `.md`).
- Whole-file exemption requires adding the repo-relative path to
  `SELF_EXEMPT_PATHS` in the scanner — use sparingly.
- CI runs `python3 scripts/security_scanner.py --strict` on every PR
  (`.github/workflows/security.yml`). Keep it green.
