.PHONY: test test-all lint format check security install-hooks pause resume pause-status

test:
	uv run pytest tests/ -v

test-all:
	uv run pytest tests/ -v -m ""

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

security:
	python3 scripts/security_scanner.py

check: lint security test

install-hooks:
	uv run --with pre-commit pre-commit install

# ── Submission kill switch ──────────────────────────────────────
# Flips system_status.accepting_reviews in Supabase. Use when
# coarse.ink needs to go offline briefly for a fix.
#
#   make pause                          # default banner
#   make pause MSG="back in 30 min"     # custom banner
#   make resume
#   make pause-status
pause:
	@scripts/kill-switch.sh pause $(if $(MSG),"$(MSG)")

resume:
	@scripts/kill-switch.sh resume

pause-status:
	@scripts/kill-switch.sh status
