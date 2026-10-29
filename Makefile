UV ?= uv
UV_CACHE_DIR ?= .uv-cache
export UV_CACHE_DIR

.PHONY: install lock-check lint format-check types test foundation verify

install:
	$(UV) sync --locked --dev

lock-check:
	$(UV) lock --check

lint:
	$(UV) run --locked ruff check .

format-check:
	$(UV) run --locked ruff format --check .

types:
	$(UV) run --locked mypy

test:
	$(UV) run --locked pytest

foundation:
	$(UV) run --locked python scripts/check_foundation.py

verify: lock-check lint format-check types test foundation
