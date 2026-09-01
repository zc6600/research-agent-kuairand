.PHONY: sync test lint typecheck quality

UV_PYTHON ?= 3.12

sync:
	uv sync --locked --python $(UV_PYTHON)

test: sync
	uv run python -m unittest discover -s tests -p 'test_*.py' -v

lint: sync
	uv run ruff check src tests

typecheck: sync
	uv run mypy

quality: sync
	uv run ruff check src tests
	uv run mypy
	uv run python -m unittest discover -s tests -p 'test_*.py' -v
