from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mlflow_ai_assurance_lab.config import load_release_policy
from mlflow_ai_assurance_lab.gate import decide


def test_regression_makes_gate_fail(tmp_path: Path) -> None:
    policy = load_release_policy()
    metrics = {name: 1.0 for name in policy.required_scorers}
    metrics["citation_source_match"] = 0.875
    decision, failed = decide(metrics, policy)
    assert decision == "FAIL"
    assert failed == ("citation_source_match",)

    results = tmp_path / "regression.json"
    results.write_text(
        json.dumps({"variants": {"governed": {"metrics": metrics}}}), encoding="utf-8"
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "mlflow_ai_assurance_lab",
            "gate",
            "--results",
            str(results),
            "--variant",
            "governed",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1
    assert "governed: FAIL" in completed.stdout


def test_missing_metric_is_not_a_success() -> None:
    policy = load_release_policy()
    try:
        decide({}, policy)
    except ValueError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("missing metrics must raise")
