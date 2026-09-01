"""Drop-in LLMClient replacements backed by headless CLI agents.

Three clients, each routing coarse review-reasoning calls through a different
headless AI CLI using the user's local subscription. Stage-specific API calls,
including multimodal extraction QA, do not use these text-only adapters:

- ``ClaudeCodeClient`` — ``claude -p`` (Claude Max / Pro subscription)
- ``CodexClient``      — ``codex exec`` (ChatGPT Plus / Pro subscription)
- ``GeminiClient``     — ``gemini -p`` (Google AI Pro / Ultra subscription)

All three implement the minimal ``LLMClient`` interface the pipeline
calls: ``complete(messages, response_model)`` and
``complete_text(messages)``. They ignore provider-specific knobs
(``reasoning_effort``, ``extra_body``, ``provider_allowlist``) since
the CLIs don't expose them.

Usage — monkey-patch ``coarse.llm.LLMClient`` to one of these before
calling ``review_paper()``. See the skills in ``~/.claude/skills/``,
``~/.codex/skills/``, and ``~/.gemini/skills/`` for working drivers.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Any

from pydantic import BaseModel

from coarse.headless_isolation import (
    CLAUDE_REQUIRED_ISOLATION_FLAGS,
    CODEX_MIN_ISOLATION_VERSION,
    CODEX_REQUIRED_ISOLATION_FLAGS,
    CODEX_REVIEW_CONFIG_OVERRIDES,
    GEMINI_MIN_ISOLATION_VERSION,
    SUBSCRIPTION_BILLING_KEYS,
    clean_subprocess_env,
    parse_cli_version,
    prepare_claude_subprocess_env,
    prepare_gemini_workspace_env,
    probe_cli_version,
)
from coarse.headless_prompt import _messages_to_prompt
from coarse.models import CODEX_MAX_EFFORT_BY_MODEL_PREFIX, HEADLESS_DEFAULT_MODELS

logger = logging.getLogger(__name__)

# Backward-compatible private export used by the existing drift guard.
_SUBSCRIPTION_BILLING_KEYS = SUBSCRIPTION_BILLING_KEYS
_clean_subprocess_env = clean_subprocess_env
_probe_cli_version = probe_cli_version

_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_JSON_ESCAPE_CHARS = frozenset('"\\/bfnrtu')
_HEX_RE = re.compile(r"^[0-9a-fA-F]{4}$")

# Shared effort-to-guidance map used by the text-level fallback when a
# host CLI's native effort flag isn't available on the installed
# version. Each value is a single sentence appended to the prompt via
# ``_effort_text_prefix``; the language mirrors what Gemini Client has
# always injected directly since Gemini CLI never exposed a flag.
_EFFORT_TEXT_GUIDANCE = {
    "low": "Keep internal reasoning brief and answer directly.",
    "medium": "Use a moderate amount of internal reasoning before answering.",
    "high": "Use thorough internal reasoning before answering.",
    "max": "Use your deepest available internal reasoning before answering.",
}


def _effort_text_prefix(effort: str) -> str:
    """Return a one-line effort-guidance block to prepend to a prompt
    when the host CLI's native effort flag isn't supported on the
    installed version.

    Kept identical in shape across all three clients so old-version
    fallback behavior is predictable — users running
    ``claude -p`` without ``--effort``, ``codex exec`` without a ``-c``
    config override, or ``gemini -p`` (which never had a native flag)
    all receive the same ``[SYSTEM] Reasoning effort: …`` preamble.
    """
    guidance = _EFFORT_TEXT_GUIDANCE.get(effort, _EFFORT_TEXT_GUIDANCE["high"])
    return f"[SYSTEM]\nReasoning effort: {effort}. {guidance}\n\n"


def _resolve_cli_bin(name: str) -> str:
    """Resolve a CLI name to its full PATH-resolved path, falling back to
    the bare name when it can't be found.

    On Windows, npm-installed CLIs (``codex``, ``gemini``) are launched through
    a ``.cmd`` shim; ``subprocess.run`` launches binaries via ``CreateProcess``
    which does NOT honor ``PATHEXT``, so a bare ``"codex"`` raises
    ``FileNotFoundError`` even though the shim is on ``PATH``. ``shutil.which``
    *does* honor ``PATHEXT`` and returns the full ``.cmd`` path, so resolving
    once at client construction makes both the ``--help`` probe and execution
    launch the path that actually exists. On a miss we keep the bare name so the
    existing
    "binary not found" guidance in ``_run_with_retry`` still fires.
    """
    return shutil.which(name) or name


def _probe_cli_help(bin_name: str, *subcommand: str) -> str:
    """Run ``<bin> [subcommand...] --help`` and return combined
    stdout + stderr as a single string, or ``""`` on any failure.

    Used to detect whether a host CLI on the user's machine exposes a
    given flag on the installed version. The callers check for
    substring membership in the returned text to decide whether to
    use a native flag or fall back to text-level injection.

    Returning an empty string on failure (missing binary, timeout,
    permission error, nonzero exit) makes the caller's
    ``"--effort" in help_text`` check default to False — i.e., if we
    can't probe, assume the old version and use the text-level
    fallback. This is the safe direction: false negatives degrade
    gracefully, false positives would crash the pipeline.

    Timeout is short (5s) because ``--help`` should never hang on a
    healthy CLI, and the whole probe runs once per class per process
    so a 5s worst case is negligible.
    """
    cmd: list[str] = [bin_name, *subcommand, "--help"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
            env=_clean_subprocess_env(),
        )
        return (result.stdout or "") + (result.stderr or "")
    except (subprocess.SubprocessError, OSError):
        return ""


# Auth-error patterns per host CLI. Substring-match only, not regex,
# because CLI auth error messages are unstructured text that changes
# shape between versions. Loose matching catches common cases; misses
# fall through to the raw stderr in the RuntimeError, which is no
# worse than today.
_AUTH_ERROR_PATTERNS: tuple[tuple[str, str], ...] = (
    # (substring to match in stderr (lowercased), user-facing hint)
    (
        "not authenticated",
        "Run `claude login` / `codex login` / `gemini auth login` to re-authenticate.",
    ),
    ("unauthorized", "Run the host CLI's login command to re-authenticate."),
    ("please log in", "Run the host CLI's login command to re-authenticate."),
    ("please login", "Run the host CLI's login command to re-authenticate."),
    ("session expired", "Your subscription session expired. Run the host CLI's login command."),
    ("session has expired", "Your subscription session expired. Run the host CLI's login command."),
    ("claude login", "Run `claude login` to re-authenticate."),
    ("codex login", "Run `codex login` to re-authenticate."),
    ("gemini login", "Run `gemini auth login` to re-authenticate."),
    ("gemini auth", "Run `gemini auth login` to re-authenticate."),
    ("not signed in", "Run the host CLI's login command to re-authenticate."),
    ("no active session", "Run the host CLI's login command to re-authenticate."),
    ("authentication required", "Run the host CLI's login command to re-authenticate."),
    ("authentication failed", "Run the host CLI's login command to re-authenticate."),
)


def _classify_cli_error(stderr: str) -> str | None:
    """Return a user-facing fix hint if ``stderr`` matches a known
    auth-failure pattern, or ``None`` otherwise.

    Used by ``_HeadlessCLIClient._run`` to prepend a ``"Run
    <host> login"`` hint to the generic nonzero-exit RuntimeError.
    Matches are case-insensitive substring checks — regex is overkill
    for a stderr classifier that needs to tolerate version drift.
    """
    if not stderr:
        return None
    lowered = stderr.lower()
    for needle, hint in _AUTH_ERROR_PATTERNS:
        if needle in lowered:
            return hint
    return None


# Transient-error patterns the retry loop treats as worth another
# attempt. Rate limits, network flakes, upstream overload — anything
# the host's backend might recover from within a few seconds. Missing
# patterns default to permanent and fail fast, which is safer than
# looping on a real bug.
_TRANSIENT_ERROR_PATTERNS: tuple[str, ...] = (
    "rate limit",
    "rate-limit",
    "rate limited",
    "too many requests",
    "429",
    "503",
    "502",
    "504",
    "temporarily unavailable",
    "temporarily overloaded",
    "service unavailable",
    "upstream error",
    "upstream timeout",
    "upstream overloaded",
    "overloaded",
    "connection reset",
    "connection refused",
    "connection timed out",
    "network error",
    "network unreachable",
    "please try again",
    "retry in",
    "eai_again",
    "econnreset",
)


def _is_transient_cli_error(stderr: str, returncode: int) -> bool:
    """True when ``stderr`` looks like a transient failure the retry
    loop should take another run at."""
    # Exit 124 is the GNU `timeout(1)` convention for "process was
    # killed because it exceeded the timeout" — on Linux some
    # wrappers surface this when the child backend took too long.
    # Not the same as our Python-level ``subprocess.TimeoutExpired``
    # (which already bubbles up directly and isn't retried here).
    if returncode == 124 and not stderr:
        return True
    if not stderr:
        return False
    lowered = stderr.lower()
    return any(pat in lowered for pat in _TRANSIENT_ERROR_PATTERNS)


# Unknown-model patterns the retry loop uses to trigger a one-time
# fallback to the host's class-default model. Separate from the
# transient list because the recovery action is different (swap
# model then retry, vs retry unchanged after a backoff).
_UNKNOWN_MODEL_PATTERNS: tuple[str, ...] = (
    "unknown model",
    "model not found",
    "invalid model",
    "no such model",
    "model does not exist",
    "unrecognized model",
)


def _is_unknown_model_error(stderr: str) -> bool:
    """True when the host CLI rejected the ``--model`` value we passed."""
    if not stderr:
        return False
    lowered = stderr.lower()
    return any(pat in lowered for pat in _UNKNOWN_MODEL_PATTERNS)


# Retry budget shared by all headless clients. 3 attempts with
# backoffs of 2s and 4s between them — cheap enough that a falsely-
# classified permanent error only wastes ~6s, small enough that a
# real transient rate limit usually clears within one hop.
_MAX_RUN_ATTEMPTS = 3
_RUN_BACKOFF_SECONDS: tuple[float, ...] = (2.0, 4.0)


# Subscription-concurrency cap. A 20-section paper with
# ``max_workers=10`` in the pipeline can spawn 10 concurrent
# ``claude -p`` subprocesses — enough to trip Claude Max / ChatGPT
# Pro / Gemini rate limits on the host side. We cap concurrent
# subprocesses per client class via a class-level semaphore,
# overridable at startup via ``COARSE_HEADLESS_CONCURRENCY``. Each
# client class (Claude / Codex / Gemini) gets its own semaphore so
# a mixed-host run doesn't have them contend against each other.
_CONCURRENCY_DEFAULT = 3
_CONCURRENCY_ENV_VAR = "COARSE_HEADLESS_CONCURRENCY"
_CONCURRENCY_MIN = 1
_CONCURRENCY_MAX = 20


def _parse_concurrency_env() -> int:
    """Read ``COARSE_HEADLESS_CONCURRENCY``, falling back to the
    default on missing / invalid / out-of-range values."""
    raw = os.environ.get(_CONCURRENCY_ENV_VAR, "").strip()
    if not raw:
        return _CONCURRENCY_DEFAULT
    try:
        n = int(raw)
    except ValueError:
        logger.warning("Ignoring invalid %s=%r (not an integer)", _CONCURRENCY_ENV_VAR, raw)
        return _CONCURRENCY_DEFAULT
    if n < _CONCURRENCY_MIN or n > _CONCURRENCY_MAX:
        logger.warning(
            "Ignoring out-of-range %s=%d (must be %d-%d)",
            _CONCURRENCY_ENV_VAR,
            n,
            _CONCURRENCY_MIN,
            _CONCURRENCY_MAX,
        )
        return _CONCURRENCY_DEFAULT
    return n


def _extract_json(text: str) -> str:
    """Extract the first balanced JSON object or array from text."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    start = None
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    if start is None:
        raise ValueError(f"no JSON found in response: {text[:200]}")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise ValueError(f"unbalanced JSON in response: {text[:200]}")


def _repair_json_string(text: str) -> str:
    """Repair common JSON issues from CLI model output.

    Headless CLIs occasionally emit otherwise-correct JSON with unescaped
    backslashes inside string values, especially when copying LaTeX like
    ``\\rho`` or ``\\frac`` verbatim from the paper. That is invalid JSON
    (`json.loads` raises ``Invalid \\escape``) even though the intended field
    value is unambiguous. Repair only string-local, non-standard escapes and
    preserve valid JSON escapes unchanged.
    """
    text = _CTRL_CHAR_RE.sub("", text).replace("\\u0000", "")
    repaired: list[str] = []
    in_str = False
    escaped = False

    for i, ch in enumerate(text):
        if not in_str:
            repaired.append(ch)
            if ch == '"':
                in_str = True
            continue

        if escaped:
            repaired.append(ch)
            escaped = False
            continue

        if ch == "\\":
            next_ch = text[i + 1] if i + 1 < len(text) else ""
            if next_ch == "u":
                hex_digits = text[i + 2 : i + 6]
                if len(hex_digits) == 4 and _HEX_RE.fullmatch(hex_digits):
                    repaired.append(ch)
                    escaped = True
                else:
                    repaired.append("\\\\")
                continue
            if next_ch in _JSON_ESCAPE_CHARS:
                repaired.append(ch)
                escaped = True
                continue
            repaired.append("\\\\")
            continue

        repaired.append(ch)
        if ch == '"':
            in_str = False

    return "".join(repaired)


class _HeadlessCLIClient:
    """Shared base for headless CLI-backed LLMClient replacements.

    Subclasses implement ``_build_cmd(self) -> list[str]`` which returns
    the command line for running the CLI in non-interactive mode with
    the prompt coming from stdin.
    """

    #: Human-readable name for error messages ("claude -p", "codex exec", ...).
    display_name: str = "headless-cli"

    #: Per-class concurrency semaphore. Lazily initialised via
    #: ``_get_semaphore`` on first use so tests can override the
    #: environment variable before the semaphore is created. Stored
    #: on each *subclass* so Claude / Codex / Gemini each get their
    #: own cap — a mixed-host run doesn't cross-contend.
    _semaphore: threading.Semaphore | None = None
    _semaphore_init_lock: threading.Lock = threading.Lock()

    def __init__(
        self,
        model: str | None = None,
        config: Any = None,
        *,
        timeout: int = 1800,
        **_unused,
    ) -> None:
        self._model = model or self.display_name
        self._config = config
        self._timeout = timeout
        self._cost_usd: float = 0.0
        self._lock = threading.Lock()
        #: Set True once the retry loop has fallen back to the class
        #: default model after an "unknown model" error. Prevents the
        #: fallback from firing more than once per instance.
        self._model_fallback_attempted: bool = False

    @classmethod
    def _get_semaphore(cls) -> threading.Semaphore:
        """Return the class-level concurrency semaphore, creating it
        from ``COARSE_HEADLESS_CONCURRENCY`` on first call. Double-
        checked locking so concurrent first-instantiations don't
        create two semaphores for the same class.
        """
        # Walk the MRO to check if *this* class has its own semaphore
        # attribute (not an inherited ``None`` from the base). Using
        # ``cls.__dict__`` avoids picking up the base's None.
        if cls.__dict__.get("_semaphore") is not None:
            return cls.__dict__["_semaphore"]  # type: ignore[return-value]
        with cls._semaphore_init_lock:
            if cls.__dict__.get("_semaphore") is None:
                cls._semaphore = threading.Semaphore(_parse_concurrency_env())
        return cls.__dict__["_semaphore"]  # type: ignore[return-value]

    def _can_fall_back_to_default_model(self) -> bool:
        """Subclasses override: return True when the current model
        differs from the class default AND a fallback hasn't yet
        been attempted."""
        return False

    def _fall_back_to_default_model(self) -> None:
        """Subclasses override: swap the current model for the
        class default and flip ``_model_fallback_attempted``."""
        self._model_fallback_attempted = True

    @property
    def model(self) -> str:
        return self._model

    @property
    def cost_usd(self) -> float:
        return self._cost_usd

    def add_cost(self, amount: float) -> None:
        """Track external costs (e.g. Perplexity search via litellm)."""
        with self._lock:
            self._cost_usd += amount

    @property
    def supports_prompt_caching(self) -> bool:
        """Report False so agents skip cache_control markers that these
        CLIs don't understand. The CLIs handle caching internally."""
        return False

    def _build_cmd(self) -> list[str]:
        raise NotImplementedError

    def _install_hint(self) -> str:
        """Return a one-line install command users can paste into a
        shell when the host CLI binary is missing. Subclasses override
        this with the host-specific package install command."""
        return "install the host CLI and make sure it is on your PATH"

    def _prepare_prompt(self, prompt: str) -> str:
        """Allow subclasses to inject host-specific prompt hints."""
        return prompt

    def _workspace_args(self, _workspace: str) -> list[str]:
        """Return host-specific arguments that bind execution to the empty workspace."""
        return []

    def _workspace_env(self, _workspace: str) -> dict[str, str]:
        """Return the review-only child environment for this invocation."""
        return _clean_subprocess_env()

    def _run(self, prompt: str, *, timeout: int | None = None) -> str:
        """Run the host CLI once with retry on transient failures.

        The retry loop is shared by all three clients:

        1. **Concurrency semaphore**: at most ``N`` subprocesses of
           this class run at once (default 3, override via
           ``COARSE_HEADLESS_CONCURRENCY``). The semaphore protects
           against Claude Max / ChatGPT Pro / Gemini rate limits
           when the pipeline spawns 10 parallel section reviews.
        2. **Attempt loop**: up to ``_MAX_RUN_ATTEMPTS`` (3) tries
           with ``_RUN_BACKOFF_SECONDS`` delays between them. Only
           failures classified as transient via
           ``_is_transient_cli_error`` are retried; everything else
           fails fast.
        3. **Permanent failures skip retry**: ``FileNotFoundError``
           (missing binary), Python-level timeout, auth-expired
           stderr, and generic non-zero exits without a transient
           pattern.
        4. **Unknown-model fallback**: on an "unknown model" error
           the loop tries once more with the class default model,
           at most once per instance.
        """
        with type(self)._get_semaphore():
            return self._run_with_retry(prompt, timeout=timeout)

    def _run_with_retry(self, prompt: str, *, timeout: int | None = None) -> str:
        # Manual attempt counter so an unknown-model fallback swap can
        # re-enter the loop WITHOUT consuming a transient-retry slot
        # AND without triggering the backoff sleep on the next
        # iteration. A for-loop would auto-increment and the `continue`
        # would land on `attempt > 0` + a mandatory 2s sleep.
        with tempfile.TemporaryDirectory(prefix="coarse-review-") as workspace:
            return self._run_attempts(prompt, workspace, timeout=timeout)

    def _run_attempts(self, prompt: str, workspace: str, *, timeout: int | None = None) -> str:
        attempt = 0
        just_fell_back = False
        last_stderr = ""
        original_user_model: str | None = None
        while attempt < _MAX_RUN_ATTEMPTS:
            if attempt > 0 and not just_fell_back:
                sleep_seconds = _RUN_BACKOFF_SECONDS[
                    min(attempt - 1, len(_RUN_BACKOFF_SECONDS) - 1)
                ]
                logger.warning(
                    "%s retry %d/%d after %.0fs backoff (stderr=%s)",
                    self.display_name,
                    attempt + 1,
                    _MAX_RUN_ATTEMPTS,
                    sleep_seconds,
                    last_stderr[:200],
                )
                time.sleep(sleep_seconds)
            just_fell_back = False

            cmd = self._build_cmd()
            workspace_args = self._workspace_args(workspace)
            if cmd and cmd[-1] == "-":
                cmd[-1:-1] = workspace_args
            else:
                cmd.extend(workspace_args)
            try:
                proc = subprocess.run(
                    cmd,
                    input=prompt,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=timeout or self._timeout,
                    check=False,
                    env=self._workspace_env(workspace),
                    cwd=workspace,
                )
            except FileNotFoundError as exc:
                raise RuntimeError(
                    f"{self.display_name} binary not found on PATH. "
                    f"Install it with: {self._install_hint()}"
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(
                    f"{self.display_name} timed out after {timeout or self._timeout}s"
                ) from exc

            if proc.returncode == 0:
                return proc.stdout

            stderr = proc.stderr or ""
            last_stderr = stderr

            auth_hint = _classify_cli_error(stderr)
            if auth_hint:
                raise RuntimeError(
                    f"{self.display_name} auth failure. {auth_hint} Raw error: {stderr[:300]}"
                )

            # Unknown-model fallback: swap to the class default and
            # re-enter the loop WITHOUT incrementing `attempt`, so the
            # fallback model still gets its full retry budget on
            # subsequent transient failures.
            if _is_unknown_model_error(stderr) and self._can_fall_back_to_default_model():
                if original_user_model is None:
                    original_user_model = (
                        getattr(self, "_claude_model", None)
                        or getattr(self, "_codex_model", None)
                        or getattr(self, "_gemini_model", None)
                    )
                self._fall_back_to_default_model()
                just_fell_back = True
                continue

            if _is_transient_cli_error(stderr, proc.returncode) and attempt < _MAX_RUN_ATTEMPTS - 1:
                attempt += 1
                continue

            suffix = ""
            if original_user_model is not None:
                suffix = (
                    f" (user-selected model {original_user_model!r} was "
                    f"rejected first; retried with default)"
                )
            raise RuntimeError(
                f"{self.display_name} exited {proc.returncode}: {stderr[:500]}{suffix}"
            )

        raise AssertionError("unreachable: _run_with_retry exited the loop")

    def complete(
        self,
        messages: list[dict],
        response_model: type[BaseModel],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 1800,
        **_kwargs,
    ) -> BaseModel:
        """Structured completion — runs the CLI and parses into response_model."""
        base_prompt = _messages_to_prompt(messages)
        schema = response_model.model_json_schema()
        prompt = (
            f"{base_prompt}\n\n"
            f"---\n\n"
            f"Respond with ONLY a JSON object matching this schema. "
            f"No prose outside the JSON, no markdown fences, no commentary. "
            f"Inside JSON string values, escape backslashes exactly as JSON "
            f"requires (for example, write \\\\left rather than \\left).\n\n"
            f"Schema:\n```json\n{json.dumps(schema, indent=2)}\n```"
        )

        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                raw = self._run(self._prepare_prompt(prompt), timeout=timeout)
                json_str = _extract_json(raw)
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    data = json.loads(_repair_json_string(json_str))
                return response_model.model_validate(data)
            except (json.JSONDecodeError, ValueError) as exc:
                last_exc = exc
                logger.warning(
                    "%s attempt %d returned invalid JSON: %s",
                    self.display_name,
                    attempt + 1,
                    exc,
                )
                continue
        raise RuntimeError(
            f"{self.display_name} failed to produce valid "
            f"{response_model.__name__} JSON after 3 attempts: {last_exc}"
        )

    def complete_text(
        self,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 1800,
        **_kwargs,
    ) -> str:
        """Unstructured text completion."""
        prompt = _messages_to_prompt(messages)
        return self._run(self._prepare_prompt(prompt), timeout=timeout).strip()


class ClaudeCodeClient(_HeadlessCLIClient):
    """LLMClient replacement backed by the ``claude -p`` CLI.

    ``--effort`` is version-gated. Older Claude Code versions reject
    the flag with ``error: unknown option '--effort'`` and die before
    running anything. We probe ``claude -p --help`` once per class on
    first use and either use the native flag (new versions) or fall
    back to text-level guidance injected via ``_prepare_prompt``
    (old versions). A real user hit this — #132's coauthor review
    caught it after a v1.3.0 preview-testing session died on every
    pipeline stage with a subprocess exit code 2.
    """

    display_name = "claude -p"

    #: Class-level cache for the ``--help`` probe result. First
    #: instantiated client probes; all subsequent clients in the same
    #: process reuse the result. Reset between tests via the
    #: ``reset_headless_probe_cache`` fixture in conftest.
    _effort_flag_probed: bool = False
    _effort_flag_supported: bool = False
    _isolation_flags_supported: bool = False

    def __init__(
        self,
        model: str | None = None,
        config: Any = None,
        *,
        claude_bin: str = "claude",
        claude_model: str = HEADLESS_DEFAULT_MODELS["claude"],
        effort: str = "high",
        timeout: int = 1800,
        **kwargs,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout, **kwargs)
        self._claude_bin = _resolve_cli_bin(claude_bin)
        self._claude_model = claude_model
        self._effort = effort

    def _install_hint(self) -> str:
        return "npm install -g @anthropic-ai/claude-code@latest (or https://claude.ai/download)"

    def _can_fall_back_to_default_model(self) -> bool:
        if self._model_fallback_attempted:
            return False
        default = HEADLESS_DEFAULT_MODELS["claude"]
        return bool(self._claude_model) and self._claude_model != default

    def _fall_back_to_default_model(self) -> None:
        default = HEADLESS_DEFAULT_MODELS["claude"]
        logger.warning(
            "Claude Code rejected model %r — falling back to default %r. "
            "Override the model with --model <name> on the next run.",
            self._claude_model,
            default,
        )
        self._claude_model = default
        self._model_fallback_attempted = True

    def _ensure_effort_probed(self) -> None:
        """Probe whether ``claude -p --help`` mentions ``--effort``,
        caching the result on the class so every subsequent client in
        the same process reuses it."""
        cls = type(self)
        if cls._effort_flag_probed:
            return
        help_text = _probe_cli_help(self._claude_bin, "-p")
        cls._effort_flag_supported = "--effort" in help_text
        cls._isolation_flags_supported = all(
            flag in help_text for flag in CLAUDE_REQUIRED_ISOLATION_FLAGS
        )
        cls._effort_flag_probed = True
        if not cls._effort_flag_supported:
            logger.warning(
                "Claude Code on this machine does not expose --effort "
                "(old version). Falling back to text-level effort "
                "injection. Upgrade Claude Code for native reasoning-"
                "effort control: npm install -g @anthropic-ai/claude-code@latest"
            )

    def _build_cmd(self) -> list[str]:
        # Claude Code already exposes the same low/medium/high/max scale we
        # want at the coarse layer, so pass it through unchanged when the
        # installed version supports --effort; otherwise drop the flag and
        # let _prepare_prompt inject the guidance as text.
        self._ensure_effort_probed()
        if not type(self)._isolation_flags_supported:
            raise RuntimeError(
                "Claude Code cannot provide the required review-only isolation. "
                "Upgrade with: npm install -g @anthropic-ai/claude-code@latest"
            )
        cmd = [
            self._claude_bin,
            "-p",
            "--safe-mode",
            "--disable-slash-commands",
            "--strict-mcp-config",
            "--mcp-config",
            '{"mcpServers":{}}',
            "--tools",
            "",
            "--permission-mode",
            "plan",
            "--no-session-persistence",
            "--model",
            self._claude_model,
            "--output-format",
            "text",
        ]
        if type(self)._effort_flag_supported:
            cmd += ["--effort", self._effort]
        return cmd

    def _prepare_prompt(self, prompt: str) -> str:
        self._ensure_effort_probed()
        if type(self)._effort_flag_supported:
            return prompt
        return _effort_text_prefix(self._effort) + prompt

    def _workspace_env(self, _workspace: str) -> dict[str, str]:
        return prepare_claude_subprocess_env()


class CodexClient(_HeadlessCLIClient):
    """LLMClient replacement backed by the ``codex exec`` CLI (ChatGPT).

    ``effort`` maps to Codex's ``model_reasoning_effort`` config
    override (low / medium / high / xhigh / max, depending on the model).
    We pass it via ``-c model_reasoning_effort=<level>`` per call so the choice is
    ephemeral and doesn't mutate the user's ``~/.codex/config.toml``.

    Review execution requires permission profiles and the current tool-disable
    controls. Older builds fail closed with an upgrade remedy rather than
    silently reverting to the legacy full-disk-readable sandbox.
    """

    display_name = "codex exec"

    #: Probe cache — see ``ClaudeCodeClient._effort_flag_probed``.
    _config_override_probed: bool = False
    _config_override_supported: bool = False

    def __init__(
        self,
        model: str | None = None,
        config: Any = None,
        *,
        codex_bin: str = "codex",
        codex_model: str | None = None,
        effort: str = "high",
        timeout: int = 1800,
        **kwargs,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout, **kwargs)
        self._codex_bin = _resolve_cli_bin(codex_bin)
        self._codex_model = codex_model
        self._effort = effort

    def _install_hint(self) -> str:
        return "npm install -g @openai/codex@latest (or https://developers.openai.com/codex/cli)"

    def _can_fall_back_to_default_model(self) -> bool:
        if self._model_fallback_attempted:
            return False
        if self._codex_model is None:
            # Already using codex's built-in default — nothing to fall back to.
            return False
        default = HEADLESS_DEFAULT_MODELS["codex"]
        return self._codex_model != default

    def _fall_back_to_default_model(self) -> None:
        default = HEADLESS_DEFAULT_MODELS["codex"]
        logger.warning(
            "Codex rejected model %r — falling back to default %r. "
            "Override the model with --model <name> on the next run.",
            self._codex_model,
            default,
        )
        self._codex_model = default
        self._model_fallback_attempted = True

    def _ensure_config_override_probed(self) -> None:
        """Probe the minimum version and flags needed for review isolation."""
        cls = type(self)
        if cls._config_override_probed:
            return
        help_text = _probe_cli_help(self._codex_bin, "exec")
        config_override_supported = any(
            marker in help_text
            for marker in (
                "-c <KEY=VALUE>",
                "-c KEY=VALUE",
                "-c key=value",
                "--config <KEY=VALUE>",
                "--config <key=value>",
                "--config KEY=VALUE",
            )
        )
        installed_version = parse_cli_version(_probe_cli_version(self._codex_bin))
        cls._config_override_supported = (
            config_override_supported
            and installed_version is not None
            and installed_version >= CODEX_MIN_ISOLATION_VERSION
            and all(flag in help_text for flag in CODEX_REQUIRED_ISOLATION_FLAGS)
        )
        cls._config_override_probed = True
        if not cls._config_override_supported:
            logger.warning(
                "Codex cannot provide the required review-only permission profile. "
                "Upgrade Codex: npm install -g @openai/codex@latest"
            )

    def _build_cmd(self) -> list[str]:
        self._ensure_config_override_probed()
        if not type(self)._config_override_supported:
            minimum = ".".join(str(part) for part in CODEX_MIN_ISOLATION_VERSION)
            raise RuntimeError(
                "Codex cannot provide the required review-only isolation. "
                f"Upgrade to Codex {minimum} or newer."
            )
        # --skip-git-repo-check: `codex exec` refuses to run when its CWD isn't
        # a trusted git repo ("Not inside a trusted directory"). The subprocess
        # coarse spawns runs from wherever the user invoked coarse-review, which
        # often isn't such a repo (handoff tempdirs, arbitrary paper dirs), so
        # pass it on every platform — it's a no-op inside a trusted repo. Unlike
        # the `-c` config override below, this flag is long-standing in codex and
        # is assumed universally supported (not version-probed).
        cmd = [
            self._codex_bin,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--strict-config",
        ]
        for override in CODEX_REVIEW_CONFIG_OVERRIDES:
            cmd += ["-c", override]
        if self._codex_model:
            cmd += ["-m", self._codex_model]
        mapped = self._effort
        if mapped == "max":
            model = (self._codex_model or HEADLESS_DEFAULT_MODELS["codex"]).lower()
            model = model.removeprefix("openai/")
            mapped = next(
                (
                    level
                    for prefix, level in CODEX_MAX_EFFORT_BY_MODEL_PREFIX
                    if model.startswith(prefix)
                ),
                "high",
            )
        cmd += ["-c", f"model_reasoning_effort={mapped!r}"]
        # Read prompt from stdin by passing '-' as the positional arg.
        cmd.append("-")
        return cmd

    def _workspace_args(self, workspace: str) -> list[str]:
        return ["-C", workspace]

    def _prepare_prompt(self, prompt: str) -> str:
        self._ensure_config_override_probed()
        return prompt


class GeminiClient(_HeadlessCLIClient):
    """LLMClient replacement backed by the ``gemini -p`` CLI.

    Gemini CLI does not expose a native reasoning-effort flag. We still
    honor coarse's low/medium/high/max selector by prepending an explicit
    effort instruction with increasing advisory thinking budgets.

    Two capabilities on Gemini CLI are version-gated:

    1. ``--approval-mode plan`` is mandatory for the review-only profile.
       Older versions fail closed instead of falling back to unrestricted
       ``--yolo`` execution.
    2. ``--output-format text`` was added when Gemini CLI grew JSON
       output support. Older versions don't have it and default to
       text output, so dropping the flag is a safe fallback.

    The class probes ``gemini --help`` and ``gemini --version`` once per
    process. Effort-level injection is already text-only and needs no probing.
    """

    display_name = "gemini -p"

    #: Probe cache — separate flags for the two version-gated knobs.
    _flag_probed: bool = False
    _approval_mode_flag_supported: bool = False
    _output_format_flag_supported: bool = False

    _EFFORT_BUDGET = {
        "low": 0,
        "medium": 4096,
        "high": 16384,
        "max": 32768,
    }

    def __init__(
        self,
        model: str | None = None,
        config: Any = None,
        *,
        gemini_bin: str = "gemini",
        gemini_model: str | None = None,
        effort: str = "high",
        approval_mode: str = "plan",
        timeout: int = 1800,
        **kwargs,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout, **kwargs)
        self._gemini_bin = _resolve_cli_bin(gemini_bin)
        self._gemini_model = gemini_model
        self._effort = effort
        self._approval_mode = approval_mode
        if approval_mode != "plan":
            raise ValueError("Gemini review stages require approval_mode='plan'")

    def _install_hint(self) -> str:
        return "npm install -g @google/gemini-cli@latest (or https://github.com/google-gemini/gemini-cli)"

    def _can_fall_back_to_default_model(self) -> bool:
        if self._model_fallback_attempted:
            return False
        if self._gemini_model is None:
            return False
        default = HEADLESS_DEFAULT_MODELS["gemini"]
        return self._gemini_model != default

    def _fall_back_to_default_model(self) -> None:
        default = HEADLESS_DEFAULT_MODELS["gemini"]
        logger.warning(
            "Gemini CLI rejected model %r — falling back to default %r. "
            "Override the model with --model <name> on the next run.",
            self._gemini_model,
            default,
        )
        self._gemini_model = default
        self._model_fallback_attempted = True

    def _ensure_flags_probed(self) -> None:
        cls = type(self)
        if cls._flag_probed:
            return
        help_text = _probe_cli_help(self._gemini_bin)
        installed_version = parse_cli_version(_probe_cli_version(self._gemini_bin))
        cls._approval_mode_flag_supported = (
            "--approval-mode" in help_text
            and "plan" in help_text
            and installed_version is not None
            and installed_version >= GEMINI_MIN_ISOLATION_VERSION
        )
        cls._output_format_flag_supported = "--output-format" in help_text
        cls._flag_probed = True
        if not cls._approval_mode_flag_supported:
            logger.warning(
                "Gemini CLI on this machine does not expose --approval-mode "
                "(old version). Review execution will fail closed. "
                "Upgrade Gemini CLI: npm install -g "
                "@google/gemini-cli@latest"
            )

    def _build_cmd(self) -> list[str]:
        self._ensure_flags_probed()
        cls = type(self)
        cmd: list[str] = [self._gemini_bin]
        if cls._approval_mode_flag_supported:
            cmd += ["--approval-mode", self._approval_mode]
        else:
            raise RuntimeError(
                "Gemini CLI cannot provide the required review-only isolation. "
                "Upgrade to a version that supports --approval-mode plan."
            )
        if cls._output_format_flag_supported:
            cmd += ["--output-format", "text"]
        if self._gemini_model:
            cmd += ["--model", self._gemini_model]
        return cmd

    def _workspace_env(self, workspace: str) -> dict[str, str]:
        return prepare_gemini_workspace_env(workspace)

    def _prepare_prompt(self, prompt: str) -> str:
        budget = self._EFFORT_BUDGET.get(self._effort, self._EFFORT_BUDGET["high"])
        guidance = {
            "low": "Keep internal reasoning short and answer directly.",
            "medium": "Use a moderate amount of internal reasoning before answering.",
            "high": "Use thorough internal reasoning before answering.",
            "max": "Use your deepest available internal reasoning before answering.",
        }.get(self._effort, "Use thorough internal reasoning before answering.")
        return (
            "[SYSTEM]\n"
            f"Reasoning effort: {self._effort}. {guidance} "
            f"Aim for roughly a {budget}-token thinking budget if supported.\n\n"
            f"{prompt}"
        )
