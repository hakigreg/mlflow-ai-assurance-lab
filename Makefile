UV ?= uv
UV_CACHE_DIR ?= .uv-cache
export UV_CACHE_DIR
export MLFLOW_DISABLE_AGENT_HINT = 1
export MLFLOW_ENABLE_TELEMETRY = false
export DO_NOT_TRACK = 1
UV_RUN = $(UV) run --locked --no-sync

.PHONY: setup install lock-check lint format-check types test foundation demo evaluate gate \
	evidence evidence-validate sample-evidence-validate verify

setup: install

install:
	$(UV) sync --locked --dev

lock-check:
	$(UV) lock --check

lint:
	$(UV_RUN) ruff check .

format-check:
	$(UV_RUN) ruff format --check .

types:
	$(UV_RUN) mypy

test:
	$(UV_RUN) pytest

foundation:
	$(UV_RUN) python scripts/check_foundation.py

demo:
	$(UV_RUN) python -m mlflow_ai_assurance_lab demo

evaluate:
	$(UV_RUN) python -m mlflow_ai_assurance_lab evaluate

gate:
	$(UV_RUN) python -m mlflow_ai_assurance_lab gate --variant governed

evidence:
	$(UV_RUN) python -m mlflow_ai_assurance_lab evidence

evidence-validate:
	$(UV_RUN) python -m mlflow_ai_assurance_lab validate-evidence

sample-evidence-validate:
	$(UV_RUN) python -m mlflow_ai_assurance_lab validate-evidence \
		--output-dir evidence/sample

verify: lock-check lint format-check types test foundation evaluate gate evidence \
	evidence-validate sample-evidence-validate
