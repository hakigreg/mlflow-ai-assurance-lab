from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from mlflow_ai_assurance_lab.config import DEFAULT_POLICY_PATH, load_release_policy
from mlflow_ai_assurance_lab.gate import GateInputError, decide


def _metrics() -> dict[str, float]:
    return {name: 1.0 for name in load_release_policy().required_scorers}


def _results(
    metrics: dict[str, Any],
    *,
    decision: str = "PASS",
    failed_metrics: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "policy_version": "release-policy-v1",
        "release_policy_sha256": hashlib.sha256(DEFAULT_POLICY_PATH.read_bytes()).hexdigest(),
        "variants": {
            "governed": {
                "variant": "governed",
                "metrics": metrics,
                "decision": decision,
                "failed_metrics": failed_metrics or [],
            }
        },
    }


def _run_gate(
    results_path: Path, policy_path: Path = DEFAULT_POLICY_PATH
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "mlflow_ai_assurance_lab",
            "gate",
            "--results",
            str(results_path),
            "--policy",
            str(policy_path),
            "--variant",
            "governed",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_regression_makes_gate_fail(tmp_path: Path) -> None:
    policy = load_release_policy()
    metrics = _metrics()
    metrics["citation_source_match"] = 0.875
    decision, failed = decide(metrics, policy)
    assert decision == "FAIL"
    assert failed == ("citation_source_match",)

    results = tmp_path / "regression.json"
    _write_json(
        results,
        _results(
            metrics,
            decision="FAIL",
            failed_metrics=["citation_source_match"],
        ),
    )
    completed = _run_gate(results)
    assert completed.returncode == 1
    assert "governed: FAIL" in completed.stdout


def test_missing_metric_is_not_a_success_at_cli_boundary(tmp_path: Path) -> None:
    metrics = _metrics()
    del metrics["citation_source_match"]
    results = tmp_path / "missing-metric.json"
    _write_json(results, _results(metrics))

    completed = _run_gate(results)

    assert completed.returncode == 2
    assert "required scorer metrics are missing" in completed.stderr
    assert "PASS" not in completed.stdout


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -0.01, 1.01, True, "1.0"])
def test_invalid_metric_values_raise_explicit_error(invalid: Any) -> None:
    metrics: dict[str, Any] = _metrics()
    metrics["citation_source_match"] = invalid

    with pytest.raises(GateInputError, match="metric 'citation_source_match'"):
        decide(metrics, load_release_policy())


def test_non_finite_metric_is_not_a_success_at_cli_boundary(tmp_path: Path) -> None:
    metrics = _metrics()
    metrics["citation_source_match"] = float("nan")
    results = tmp_path / "nan-metric.json"
    _write_json(results, _results(metrics))

    completed = _run_gate(results)

    assert completed.returncode == 2
    assert "must be finite" in completed.stderr
    assert "PASS" not in completed.stdout


def test_inconsistent_policy_is_not_a_success_at_cli_boundary(tmp_path: Path) -> None:
    policy_payload = json.loads(DEFAULT_POLICY_PATH.read_text(encoding="utf-8"))
    del policy_payload["thresholds"]["citation_source_match"]
    policy_path = tmp_path / "inconsistent-policy.json"
    _write_json(policy_path, policy_payload)
    results = tmp_path / "results.json"
    _write_json(results, _results(_metrics()))

    completed = _run_gate(results, policy_path)

    assert completed.returncode == 2
    assert "scorers and threshold keys must match" in completed.stderr
    assert "PASS" not in completed.stdout


def test_recorded_pass_cannot_override_recomputed_failure(tmp_path: Path) -> None:
    metrics = _metrics()
    metrics["citation_source_match"] = 0.0
    results = tmp_path / "false-pass.json"
    _write_json(results, _results(metrics, decision="PASS"))

    completed = _run_gate(results)

    assert completed.returncode == 2
    assert "recorded decision 'PASS' does not match recomputed 'FAIL'" in completed.stderr
    assert "PASS" not in completed.stdout


def test_stale_policy_binding_is_not_accepted(tmp_path: Path) -> None:
    payload = copy.deepcopy(_results(_metrics()))
    payload["release_policy_sha256"] = "0" * 64
    results = tmp_path / "stale-policy-binding.json"
    _write_json(results, payload)

    completed = _run_gate(results)

    assert completed.returncode == 2
    assert "release_policy_sha256 is stale or inconsistent" in completed.stderr
    assert "PASS" not in completed.stdout
