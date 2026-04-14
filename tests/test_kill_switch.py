"""Regression tests for the submission kill switch."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _load_kill_switch_module():
    module_path = REPO_ROOT / "scripts" / "kill_switch.py"
    spec = importlib.util.spec_from_file_location("kill_switch", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kill_switch"] = module
    spec.loader.exec_module(module)
    return module


def test_load_env_file_strips_wrapping_quotes(tmp_path: Path) -> None:
    kill_switch = _load_kill_switch_module()
    env_path = tmp_path / ".env.local"
    env_path.write_text(
        "\n".join(
            [
                'NEXT_PUBLIC_SUPABASE_URL="https://example.supabase.co"',
                "SUPABASE_SERVICE_KEY='service-key'",
            ]
        ),
        encoding="utf-8",
    )

    values = kill_switch.load_env_file(env_path)

    assert values["NEXT_PUBLIC_SUPABASE_URL"] == "https://example.supabase.co"
    assert values["SUPABASE_SERVICE_KEY"] == "service-key"


def test_resolve_config_prefers_environment_when_both_values_set(tmp_path: Path) -> None:
    kill_switch = _load_kill_switch_module()
    env_path = tmp_path / ".env.local"
    env_path.write_text(
        "\n".join(
            [
                "NEXT_PUBLIC_SUPABASE_URL=https://file.supabase.co",
                "SUPABASE_SERVICE_KEY=file-key",
            ]
        ),
        encoding="utf-8",
    )

    config = kill_switch.resolve_config(
        env={
            "SUPABASE_URL": "https://env.supabase.co",
            "SUPABASE_SERVICE_KEY": "env-key",
        },
        env_path=env_path,
    )

    assert config.supabase_url == "https://env.supabase.co"
    assert config.service_key == "env-key"


def test_resolve_config_falls_back_to_env_local_when_shell_empty(tmp_path: Path) -> None:
    kill_switch = _load_kill_switch_module()
    env_path = tmp_path / ".env.local"
    env_path.write_text(
        "\n".join(
            [
                "NEXT_PUBLIC_SUPABASE_URL=https://file.supabase.co",
                "SUPABASE_SERVICE_KEY=file-key",
            ]
        ),
        encoding="utf-8",
    )

    config = kill_switch.resolve_config(env={}, env_path=env_path)

    assert config.supabase_url == "https://file.supabase.co"
    assert config.service_key == "file-key"


def test_resolve_config_rejects_mixed_env_and_file_sources(tmp_path: Path) -> None:
    kill_switch = _load_kill_switch_module()
    env_path = tmp_path / ".env.local"
    env_path.write_text(
        "\n".join(
            [
                "NEXT_PUBLIC_SUPABASE_URL=https://file.supabase.co",
                "SUPABASE_SERVICE_KEY=file-key",
            ]
        ),
        encoding="utf-8",
    )

    try:
        kill_switch.resolve_config(
            env={"SUPABASE_URL": "https://env.supabase.co"},
            env_path=env_path,
        )
    except RuntimeError as exc:
        assert "Set both SUPABASE_URL and SUPABASE_SERVICE_KEY" in str(exc)
    else:
        raise AssertionError("resolve_config should reject mixed env/file configuration")


def test_set_paused_sends_patch_payload(monkeypatch) -> None:
    kill_switch = _load_kill_switch_module()
    calls: list[dict[str, object]] = []

    def fake_request_json(method, url, service_key, *, payload=None):
        calls.append(
            {
                "method": method,
                "url": url,
                "service_key": service_key,
                "payload": payload,
            }
        )
        assert payload is not None
        return [
            {
                "accepting_reviews": payload["accepting_reviews"],
                "banner_message": payload["banner_message"],
                "updated_at": payload["updated_at"],
            }
        ]

    monkeypatch.setattr(kill_switch, "request_json", fake_request_json)

    row = kill_switch.set_paused(
        kill_switch.Config("https://example.supabase.co", "service-key"),
        accepting_reviews=False,
        banner_message="Paused for maintenance",
    )

    assert row["accepting_reviews"] is False
    assert row["banner_message"] == "Paused for maintenance"
    assert len(calls) == 1
    assert calls[0]["method"] == "PATCH"
    assert calls[0]["url"] == (
        "https://example.supabase.co/rest/v1/system_status"
        "?id=eq.1&select=accepting_reviews,banner_message,updated_at"
    )
    assert calls[0]["service_key"] == "service-key"
    payload = calls[0]["payload"]
    assert isinstance(payload, dict)
    assert payload["accepting_reviews"] is False
    assert payload["banner_message"] == "Paused for maintenance"
    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
        str(payload["updated_at"]),
    )


def test_makefile_exposes_pause_commands() -> None:
    text = _read("Makefile")

    assert (
        ".PHONY: test test-all lint format check security install-hooks pause resume pause-status"
        in text
    )
    assert 'pause:\n\t@python3 scripts/kill_switch.py pause $(if $(MSG),"$(MSG)")' in text
    assert "resume:\n\t@python3 scripts/kill_switch.py resume" in text
    assert "pause-status:\n\t@python3 scripts/kill_switch.py status" in text


def test_paid_routes_use_shared_pause_helper_and_early_return() -> None:
    route_paths = [
        "web/src/app/api/presign/route.ts",
        "web/src/app/api/submit/route.ts",
        "web/src/app/api/mcp-extract/route.ts",
        "web/src/app/api/cli-handoff/route.ts",
    ]

    for path in route_paths:
        text = _read(path)
        assert "getSubmissionPauseResponse" in text
        assert "const paused = await getSubmissionPauseResponse(" in text
        assert "if (paused) return paused;" in text


def test_mcp_handoff_route_stays_open_for_inflight_reviews() -> None:
    text = _read("web/src/app/api/mcp-handoff/route.ts")

    assert "getSubmissionPauseResponse" not in text
    assert "const paused = await getSubmissionPauseResponse(" not in text


def test_handoff_landing_page_checks_pause_before_token_lookup() -> None:
    text = _read("web/src/app/h/[token]/route.ts")

    assert "getSubmissionPauseState" in text
    assert "if (!pauseState.accepting)" in text
    assert "renderPausedLandingPage" in text
    assert text.index("getSubmissionPauseState") < text.index('.from("mcp_handoff_tokens")')


def test_system_status_helper_fails_closed() -> None:
    text = _read("web/src/lib/systemStatus.ts")

    assert "DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE" in text
    assert "accepting: false" in text
    assert "message: DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE" in text


def test_status_route_fails_closed() -> None:
    text = _read("web/src/app/api/status/route.ts")

    assert "const statusUnavailable = Boolean(statusResult.error || !statusResult.data);" in text
    assert "const serviceUnavailable = statusUnavailable || Boolean(activeCountError);" in text
    assert "DEFAULT_SUBMISSIONS_UNAVAILABLE_MESSAGE" in text


def test_home_page_refreshes_system_status() -> None:
    text = _read("web/src/app/page.tsx")

    assert 'fetch("/api/status", { cache: "no-store" })' in text
    assert 'window.addEventListener("focus", handleFocus);' in text
    assert 'document.addEventListener("visibilitychange", handleVisibilityChange);' in text
    assert "window.setInterval(refreshSystemStatus, 30000);" in text
