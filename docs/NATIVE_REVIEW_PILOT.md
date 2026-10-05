# Native app review pilot

The opt-in pilot runs Coarse's existing review pipeline with native Codex or
Claude Code subagents providing its reasoning. The Python coordinator exports
model requests as tasks and replays previously accepted, typed responses until
it reaches the next unanswered requests. It never starts a provider CLI or a
paid reasoning client. The existing headless runner remains the default.

## Entry points

The repository supplies a dual-host plugin at `plugins/coarse-native-review`
and the same skill bundled in the Python package. The helper installs the native
skill alongside the existing `coarse-review` skill:

```sh
uv run coarse-native install-skill --host codex
uv run coarse-native install-skill --host claude
```

Read the returned skill path in the app. Local development uses `uv run` from
this repository; preview handoffs use the `dev` Git package. Preparation returns
a `runner_prefix` pinned to the resolved Git commit, or to the current Python
environment for local installs. Use that prefix for all subsequent commands.
This pilot is not included in the released PyPI 1.9.6 package.

```sh
uv run coarse-native prepare --paper paper.md --host codex --workspace .coarse-native/example
uv run coarse-native next --workspace .coarse-native/example
uv run coarse-native submit --workspace .coarse-native/example --task TASK_ID \
  --response /absolute/response.json --agent-id ACTUAL_NATIVE_AGENT_ID
uv run coarse-native status --workspace .coarse-native/example
```

Each pending task contains the original prompt messages and Pydantic-derived
JSON schema. The native coordinator sends those to bounded subagents, saves
returned JSON, submits it for validation, then advances again. `inherit` uses
the app's current model and effort; explicit settings require matching
host-reported submission receipts. This is provenance supplied by the host,
not independent model or token-usage attestation. Subscription usage remains
`null` when unavailable.

## Preserved review behavior

The shared `review_paper` function still controls metadata, math detection,
calibration, contribution extraction, overview, completeness, section reviews,
proof verification, cross-section synthesis, editorial filtering, quote
verification/repair, and rendering. Its default execution path is unchanged.
The optional runtime is keyword-only, preserving existing positional callers.

Native literature tasks use app web tools and explicitly record an unavailable
search. They do not invoke Perplexity. The website disables native pilot
selection when paid deep literature search is selected. Native results are not
assumed equivalent to the headless runner's reviews merely because their
schemas match; compare findings on the same prepared text before promoting the
pilot to a default.

PDF preparation uses existing OCR configuration, or `--pre-extracted paper.md`.
The pilot does not automatically call the paid vision QA model. The native host
must inspect the PDF against the prepared text and record the check:

```sh
uv run coarse-native confirm-extraction --workspace .coarse-native/example \
  --agent-id ACTUAL_INSPECTOR_ID --notes 'Inspection performed and limitations'
```

PDF publication is blocked until this host-reported inspection is recorded.

## Checkpoints and publication

Workspaces contain a source snapshot, prepared Markdown, immutable task and
response JSON, native agent receipts, and eventual `review.json`/`review.md`.
The source and engine fingerprints prevent replay against changed code or text.
Atomic writes and an operating-system lock protect updates; a crashed process
releases its lock. The directory is private and includes a deny-all `.gitignore`.
Handoff capabilities stay in a separate private `handoff.json`; never include
that file or unrelated project context in reviewer subagent prompts.

Pending tasks use a dedicated suspension signal that bypasses optional-stage
error fallbacks, so unanswered work cannot silently become a skipped review
stage. Concurrent tasks are consumed in scheduled order during replay, making
downstream prompts independent of completion timing. Accepted answers cannot
be edited in place. Start a new workspace for a revised review.

For a website review, use `prepare --handoff URL` and publish only after `ready`:

```sh
uv run coarse-native publish --workspace .coarse-native/example
```

No network publication occurs during prepare, next, or submit. Confirmed
publication is locally idempotent. Before sending, the checkpoint records an
uncertain outcome; a lost acknowledgement requires website inspection rather
than a blind retry. A local-paper run has no publication capability.

Paper readers should receive only their task messages and schema and should
not use tools. Only literature tasks need native web tools. Host permissions
still apply: this pilot's instructions are not an independent OS sandbox for
native subagents. Keep the coordinator's credentials and filesystem access out
of the review task context.

## Preview activation

Set `NEXT_PUBLIC_NATIVE_REVIEW_PILOT=1` only for the `dev` preview deployment.
After selecting Codex or Claude Code on the website, enable **Use native app
review (pilot)**. The copied prompt installs/loads the native skill and starts
preparation; the existing option remains available. Gemini retains its existing
handoff. Production has no native toggle unless the feature is explicitly enabled.

Validation combines normal CI, real local pipeline replay with fixture answers,
real native-agent evaluation, and preview browser/handoff tests. Distinguish
fixture transport checks from reviews generated by actual native agents, and
record host-specific limitations rather than claiming both app workflows were
observed when only one was exercised.
