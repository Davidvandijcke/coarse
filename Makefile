.PHONY: test test-all lint format check security install-hooks

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
