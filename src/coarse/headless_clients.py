"""Drop-in LLMClient replacements backed by headless CLI agents.

Three clients, each routing every coarse pipeline LLM call through a
different headless AI CLI using the user's local subscription:

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
import subprocess
import threading
from typing import Any

from pydantic import BaseModel

from coarse.models import HEADLESS_DEFAULT_MODELS

logger = logging.getLogger(__name__)

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
            timeout=5,
            check=False,
            env=_clean_subprocess_env(),
        )
        return (result.stdout or "") + (result.stderr or "")
    except (subprocess.SubprocessError, OSError):
        return ""


# Env vars each host CLI sets when spawning subprocesses. Stripping them
# before spawning a sibling/child CLI keeps nested sessions from seeing
# shared state (auth, session IDs, ports) belonging to the outer host.
_HOST_ENV_VARS = (
    # Claude Code
    "CLAUDECODE",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_EXECPATH",
    "CLAUDE_CODE_SSE_PORT",
    "CLAUDE_CODE_SESSION_ID",
    # Codex CLI
    "CODEX_SESSION_ID",
    "CODEX_INTERNAL",
    # Gemini CLI
    "GEMINI_SESSION_ID",
    "GEMINI_CLI_INTERNAL",
)

# Provider API keys that redirect a host CLI from subscription billing
# to pay-per-token API billing. The subscription-handoff flow exists
# SPECIFICALLY so users can run reviews on their Claude Code / Codex
# / Gemini CLI subscription — if any of these vars is set in the
# launching shell, the CLI's documented behavior is to bill the key
# holder instead, which silently charges the user's API account for
# every call in the pipeline. We strip them inside the subprocess env
# ONLY (the parent shell is unchanged) so the host CLI falls back to
# its subscription OAuth credential. The parent Python process still
# has `OPENROUTER_API_KEY` available via `os.environ` for its own
# OpenRouter-backed extraction and literature-search paths, which
# aren't part of the subprocess env.
#
# See "Claude Code → Authentication" docs: "If ANTHROPIC_API_KEY is
# set, Claude Code uses it instead of your subscription."
_SUBSCRIPTION_BILLING_KEYS = (
    # Claude Code → Anthropic subscription
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    # Codex CLI → ChatGPT / OpenAI subscription
    "OPENAI_API_KEY",
    # Gemini CLI → Google AI subscription
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)


def _clean_subprocess_env() -> dict[str, str]:
    """Return a copy of os.environ with host-CLI session markers AND
    provider API keys stripped.

    Two classes of variable get removed:

    1. ``_HOST_ENV_VARS`` — session/entrypoint markers Claude Code,
       Codex, and Gemini set for their own internal use. Stripping
       keeps nested sessions from inheriting shared state.
    2. ``_SUBSCRIPTION_BILLING_KEYS`` — provider API keys that would
       redirect the host CLI from subscription billing to API-key
       billing. Critical for the subscription-handoff flow: if the
       launching shell has ``ANTHROPIC_API_KEY`` set, Claude Code
       bills the API key for every call in the pipeline instead of
       the user's Claude Code subscription. Stripping inside the
       subprocess env forces OAuth/subscription auth. Parent shell
       is unchanged, and ``OPENROUTER_API_KEY`` (used by the parent
       Python process for extraction + literature search) is
       deliberately preserved — it's never inherited by the host CLI
       subprocess anyway.
    """
    env = dict(os.environ)
    for var in _HOST_ENV_VARS:
        env.pop(var, None)
    for var in _SUBSCRIPTION_BILLING_KEYS:
        env.pop(var, None)
    return env


def _messages_to_prompt(messages: list[dict]) -> str:
    """Flatten a chat-completions-style messages list into one prompt."""
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")
        if isinstance(content, list):
            text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
            content = "\n".join(text_parts)
        parts.append(f"[{role}]\n{content}")
    return "\n\n".join(parts)


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

    def _prepare_prompt(self, prompt: str) -> str:
        """Allow subclasses to inject host-specific prompt hints."""
        return prompt

    def _run(self, prompt: str, *, timeout: int | None = None) -> str:
        cmd = self._build_cmd()
        try:
            proc = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout or self._timeout,
                check=False,
                env=_clean_subprocess_env(),
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"{self.display_name} timed out after {timeout or self._timeout}s"
            ) from exc
        if proc.returncode != 0:
            raise RuntimeError(f"{self.display_name} exited {proc.returncode}: {proc.stderr[:500]}")
        return proc.stdout

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
        self._claude_bin = claude_bin
        self._claude_model = claude_model
        self._effort = effort

    def _ensure_effort_probed(self) -> None:
        """Probe whether ``claude -p --help`` mentions ``--effort``,
        caching the result on the class so every subsequent client in
        the same process reuses it."""
        cls = type(self)
        if cls._effort_flag_probed:
            return
        help_text = _probe_cli_help(self._claude_bin, "-p")
        cls._effort_flag_supported = "--effort" in help_text
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
        cmd = [
            self._claude_bin,
            "-p",
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


class CodexClient(_HeadlessCLIClient):
    """LLMClient replacement backed by the ``codex exec`` CLI (ChatGPT).

    ``effort`` maps to Codex's ``model_reasoning_effort`` config
    override (minimal / low / medium / high). We pass it via ``-c
    model_reasoning_effort=<level>`` per call so the choice is
    ephemeral and doesn't mutate the user's ``~/.codex/config.toml``.

    The ``-c KEY=VALUE`` flag itself is version-gated — older Codex
    builds (pre-``exec`` subcommand overhaul) didn't ship it. We
    probe ``codex exec --help`` once per class and fall back to
    text-level effort injection if ``-c`` isn't mentioned. Symmetric
    with the ``ClaudeCodeClient`` pattern.
    """

    display_name = "codex exec"

    #: Probe cache — see ``ClaudeCodeClient._effort_flag_probed``.
    _config_override_probed: bool = False
    _config_override_supported: bool = False

    # coarse-level effort name → codex model_reasoning_effort value.
    # Avoid "minimal" because current Codex builds reject web_search under
    # that setting, which breaks nested codex exec calls inside coarse.
    _EFFORT_MAP = {
        "low": "low",
        "medium": "medium",
        "high": "high",
        "max": "high",
    }

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
        self._codex_bin = codex_bin
        self._codex_model = codex_model
        self._effort = effort

    def _ensure_config_override_probed(self) -> None:
        """Probe whether ``codex exec --help`` mentions ``-c`` config
        override support, caching the result on the class."""
        cls = type(self)
        if cls._config_override_probed:
            return
        help_text = _probe_cli_help(self._codex_bin, "exec")
        # Look for any of the canonical forms Codex uses to document the
        # config override flag across versions. The probe is generous
        # because different Codex releases format --help differently;
        # we'd rather match too loosely and occasionally send -c to a
        # version that ignores unknown keys than miss a version that
        # does support it.
        cls._config_override_supported = any(
            marker in help_text
            for marker in (
                "-c <KEY=VALUE>",
                "-c KEY=VALUE",
                "-c key=value",
                "--config <KEY=VALUE>",
                "--config KEY=VALUE",
            )
        )
        cls._config_override_probed = True
        if not cls._config_override_supported:
            logger.warning(
                "Codex on this machine does not expose `-c KEY=VALUE` "
                "config override (old version). Falling back to text-"
                "level effort injection. Upgrade Codex for native "
                "reasoning-effort control: npm install -g @openai/codex@latest"
            )

    def _build_cmd(self) -> list[str]:
        self._ensure_config_override_probed()
        cmd = [self._codex_bin, "exec"]
        if self._codex_model:
            cmd += ["-m", self._codex_model]
        if type(self)._config_override_supported:
            mapped = self._EFFORT_MAP.get(self._effort, self._effort)
            cmd += ["-c", f"model_reasoning_effort={mapped!r}"]
        # Read prompt from stdin by passing '-' as the positional arg.
        cmd.append("-")
        return cmd

    def _prepare_prompt(self, prompt: str) -> str:
        self._ensure_config_override_probed()
        if type(self)._config_override_supported:
            return prompt
        return _effort_text_prefix(self._effort) + prompt


class GeminiClient(_HeadlessCLIClient):
    """LLMClient replacement backed by the ``gemini -p`` CLI.

    Gemini CLI does not expose a native reasoning-effort flag. We still
    honor coarse's low/medium/high/max selector by prepending an explicit
    effort instruction with increasing advisory thinking budgets.

    Two flags on Gemini CLI are version-gated:

    1. ``--approval-mode yolo`` (newer) vs. the legacy ``--yolo``
       toggle (older). Both do the same thing — auto-approve every
       tool call — but older Gemini CLI versions reject the newer
       name with "unknown argument".
    2. ``--output-format text`` was added when Gemini CLI grew JSON
       output support. Older versions don't have it and default to
       text output, so dropping the flag is a safe fallback.

    The class probes ``gemini --help`` once per process and picks the
    right flag set. Effort-level injection is already text-only and
    needs no probing.
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
        approval_mode: str = "yolo",
        timeout: int = 1800,
        **kwargs,
    ) -> None:
        super().__init__(model=model, config=config, timeout=timeout, **kwargs)
        self._gemini_bin = gemini_bin
        self._gemini_model = gemini_model
        self._effort = effort
        self._approval_mode = approval_mode

    def _ensure_flags_probed(self) -> None:
        cls = type(self)
        if cls._flag_probed:
            return
        help_text = _probe_cli_help(self._gemini_bin)
        cls._approval_mode_flag_supported = "--approval-mode" in help_text
        cls._output_format_flag_supported = "--output-format" in help_text
        cls._flag_probed = True
        if not cls._approval_mode_flag_supported:
            logger.warning(
                "Gemini CLI on this machine does not expose --approval-mode "
                "(old version). Falling back to the legacy --yolo flag. "
                "Upgrade Gemini CLI for the full flag set: npm install -g "
                "@google/gemini-cli@latest"
            )

    def _build_cmd(self) -> list[str]:
        self._ensure_flags_probed()
        cls = type(self)
        cmd: list[str] = [self._gemini_bin]
        if cls._approval_mode_flag_supported:
            cmd += ["--approval-mode", self._approval_mode]
        else:
            # Legacy toggle — same semantics, just the older name.
            cmd.append("--yolo")
        if cls._output_format_flag_supported:
            cmd += ["--output-format", "text"]
        if self._gemini_model:
            cmd += ["--model", self._gemini_model]
        return cmd

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
