"""Test-only startup hook for ``coarse review-parallel`` subprocess tests.

Python imports ``sitecustomize`` from the first ``sys.path`` entry that has
one. Tests put this directory on ``PYTHONPATH`` so both the parent CLI and
every ``-m coarse.cli_parallel`` worker start with the paid boundary
(pipeline, LLM client, extraction, extraction QA, API keys) replaced by the
fakes in ``_coarse_fakes.py``. Production code has no hook for this; the
swap happens entirely here, before any ``coarse`` import.

The hook is inert unless ``COARSE_FAKE_TRACE`` is set. Either way it
chain-loads the ``sitecustomize.py`` this file shadows (Homebrew and some
distros ship one in the stdlib directory).
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _chain_load_shadowed() -> None:
    for entry in sys.path:
        if not entry:
            continue
        try:
            candidate = Path(entry).resolve() / "sitecustomize.py"
        except OSError:
            continue
        if candidate.parent == _HERE or not candidate.is_file():
            continue
        spec = importlib.util.spec_from_file_location("_shadowed_sitecustomize", candidate)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return


if os.environ.get("COARSE_FAKE_TRACE"):
    sys.path.insert(0, str(_HERE))
    import _coarse_fakes

    _coarse_fakes.install()

_chain_load_shadowed()
