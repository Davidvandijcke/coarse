"""Known-advisory floors for the locked and deployed Python dependency sets."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Minimum fixed releases from the advisory set audited on 2026-09-01.
LOCK_FLOORS = {
    "aiohttp": "3.14.3",
    "click": "8.3.3",
    "docling": "2.94.0",
    "docling-core": "2.74.1",
    "idna": "3.15",
    "litellm": "1.84.0",
    "lxml": "6.1.0",
    "pillow": "12.3.0",
    "pydantic-settings": "2.14.2",
    "setuptools": "83.0.0",
    "soupsieve": "2.8.4",
    "torch": "2.13.0",
    "transformers": "5.10.0",
    "urllib3": "2.7.0",
}

MODAL_FLOORS = (
    "litellm>=1.84.0",
    "aiohttp>=3.14.3",
    "click>=8.3.3",
    "docling>=2.94.0",
    "docling-core>=2.74.1",
    "lxml>=6.1.0",
    "pillow>=12.3.0",
    "soupsieve>=2.8.4",
    "transformers>=5.10,<6",
    "urllib3>=2.7.0",
)


def _release_tuple(value: str) -> tuple[int, ...]:
    match = re.fullmatch(r"(\d+(?:\.\d+)*)", value)
    assert match, f"security floor expects a plain numeric release, got {value!r}"
    return tuple(int(part) for part in match.group(1).split("."))


def _at_least(actual: str, floor: str) -> bool:
    actual_parts = _release_tuple(actual)
    floor_parts = _release_tuple(floor)
    width = max(len(actual_parts), len(floor_parts))
    return actual_parts + (0,) * (width - len(actual_parts)) >= floor_parts + (0,) * (
        width - len(floor_parts)
    )


def test_every_locked_platform_variant_meets_known_advisory_floors() -> None:
    with (REPO_ROOT / "uv.lock").open("rb") as handle:
        lock = tomllib.load(handle)

    versions: dict[str, list[str]] = {}
    for package in lock["package"]:
        versions.setdefault(package["name"], []).append(package["version"])

    for package, floor in LOCK_FLOORS.items():
        assert package in versions, (
            f"{package} disappeared from uv.lock; revisit its security floor"
        )
        for actual in versions[package]:
            assert _at_least(actual, floor), (
                f"{package}=={actual} is below the audited fixed floor {floor}"
            )


def test_published_dependency_metadata_carries_direct_security_floors() -> None:
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    for requirement in (
        "litellm>=1.84.0",
        "aiohttp>=3.14.3",
        "click>=8.3.3",
        "urllib3>=2.7.0",
    ):
        assert requirement in project["dependencies"]

    docling = project["optional-dependencies"]["docling"]
    for requirement in (
        "docling>=2.94.0",
        "docling-core>=2.74.1",
        "lxml>=6.1.0",
        "pillow>=12.3.0",
        "soupsieve>=2.8.4",
        "transformers>=5.10,<6",
    ):
        assert requirement in docling


def test_modal_image_carries_known_high_severity_floors() -> None:
    source = (REPO_ROOT / "deploy" / "modal_worker.py").read_text(encoding="utf-8")
    for requirement in MODAL_FLOORS:
        assert f'"{requirement}"' in source

