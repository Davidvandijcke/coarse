#!/usr/bin/env python3
"""Export the canonical pipeline spec for the web estimator."""

from __future__ import annotations

import json
from pathlib import Path

from coarse.pipeline_spec import export_web_spec


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_path = repo_root / "web" / "src" / "data" / "pipelineSpec.json"
    out_path.write_text(json.dumps(export_web_spec(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
