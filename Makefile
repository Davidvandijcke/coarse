.PHONY: test test-all lint format check

test:
	uv run pytest tests/ -v

test-all:
	uv run pytest tests/ -v -m ""

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

check: lint test
