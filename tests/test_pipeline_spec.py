"""Tests for the canonical pipeline stage spec."""

from __future__ import annotations

import json
from pathlib import Path

from coarse.pipeline_spec import (
    MAX_REVIEWABLE_SECTIONS,
    estimate_cross_section_count,
    estimate_math_section_count,
    estimate_section_count,
    export_web_spec,
)


def test_section_count_caps_at_runtime_limit():
    assert estimate_section_count(999_999) == MAX_REVIEWABLE_SECTIONS


def test_math_and_cross_section_heuristics_are_stable():
    assert estimate_math_section_count(8) == 2
    assert estimate_cross_section_count(5) == 0
    assert estimate_cross_section_count(6) == 1


def test_exported_web_spec_matches_checked_in_json():
    repo_root = Path(__file__).resolve().parents[1]
    json_path = repo_root / "web" / "src" / "data" / "pipelineSpec.json"
    checked_in = json.loads(json_path.read_text())
    assert checked_in == export_web_spec()
