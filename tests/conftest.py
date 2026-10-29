from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from mlflow_ai_assurance_lab.tracking import configure_offline_tracking


@pytest.fixture(scope="session")
def tracking_runtime(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    runtime = tmp_path_factory.mktemp("mlflow-test-runtime")
    configure_offline_tracking(runtime)
    yield runtime
