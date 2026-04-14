"""Re-export contract for ``coarse.claude_code_client``.

The module is a back-compat shim that forwards a handful of names from
``coarse.headless_clients``. These tests pin that the shim stays a
strict re-export of the canonical symbols — if someone adds new state
or renames one of the forwarded names, this test fails before any
downstream importer breaks.
"""

from coarse import claude_code_client as shim
from coarse import headless_clients as canonical


def test_claude_code_client_reexports_canonical_symbols():
    assert shim.ClaudeCodeClient is canonical.ClaudeCodeClient
    assert shim._clean_subprocess_env is canonical._clean_subprocess_env
    assert shim._extract_json is canonical._extract_json
    assert shim._messages_to_prompt is canonical._messages_to_prompt
