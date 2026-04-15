"""Back-compat re-export. Use ``coarse.headless_clients`` directly in new code."""

from coarse.headless_clients import (  # noqa: F401
    ClaudeCodeClient,
    _clean_subprocess_env,
    _extract_json,
    _messages_to_prompt,
)
