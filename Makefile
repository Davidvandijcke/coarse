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

pause:
	@python3 scripts/kill_switch.py pause $(if $(MSG),"$(MSG)")

resume:
	@python3 scripts/kill_switch.py resume

pause-status:
	@python3 scripts/kill_switch.py status
