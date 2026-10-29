"""MLflow-backed offline comparison and normalized evaluation results."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import mlflow
from mlflow.genai import evaluate
from mlflow.genai.evaluation.entities import EvaluationResult

from mlflow_ai_assurance_lab.application import PolicyAssistant
from mlflow_ai_assurance_lab.config import (
    DEFAULT_CORPUS_PATH,
    DEFAULT_DATASET_PATH,
    DEFAULT_POLICY_PATH,
    load_release_policy,
)
from mlflow_ai_assurance_lab.domain import Variant, VariantResult
from mlflow_ai_assurance_lab.gate import decide
from mlflow_ai_assurance_lab.redaction import contains_sensitive_marker
from mlflow_ai_assurance_lab.scorers import offline_scorers
from mlflow_ai_assurance_lab.tracking import configure_offline_tracking, managed_dataset

DEFAULT_RUNTIME_DIR = Path("artifacts/mlflow")
DEFAULT_RESULTS_PATH = Path("artifacts/evaluation/latest.json")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize_metrics(result: EvaluationResult) -> dict[str, float]:
    normalized: dict[str, float] = {}
    for key, value in result.metrics.items():
        name = key.removesuffix("/mean")
        normalized[name] = round(float(value), 6)
    return normalized


def _case_results(frame: Any) -> tuple[dict[str, Any], ...]:
    scorer_names = tuple(scorer.name for scorer in offline_scorers())
    cases: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        request = cast(dict[str, Any], row["request"])
        response = cast(dict[str, Any], row["response"])
        scores = {name: float(row[f"{name}/value"]) for name in scorer_names}
        cases.append(
            {
                "case_id": str(request["case_id"]),
                "trace_id": str(row["trace_id"]),
                "action": str(response["action"]),
                "citations": list(response["citations"]),
                "scores": scores,
            }
        )
    return tuple(sorted(cases, key=lambda item: str(item["case_id"])))


def _assert_trace_redaction(frame: Any) -> None:
    for trace in frame["trace"]:
        if contains_sensitive_marker(str(trace)):
            raise RuntimeError("trace redaction policy violation: sensitive marker persisted")


def evaluate_variant(variant: Variant, runtime_dir: Path) -> VariantResult:
    experiment_id = configure_offline_tracking(runtime_dir)
    dataset = managed_dataset(experiment_id)
    assistant = PolicyAssistant(variant)
    result = evaluate(
        data=dataset,
        predict_fn=assistant.ask,
        scorers=offline_scorers(),
    )
    if result.result_df is None:
        raise RuntimeError("MLflow evaluation returned no per-case results")
    _assert_trace_redaction(result.result_df)
    metrics = _normalize_metrics(result)
    decision, failed_metrics = decide(metrics, load_release_policy())
    cases = _case_results(result.result_df)
    trace_ids = tuple(str(case["trace_id"]) for case in cases)
    if len(trace_ids) != len(dataset.to_df()):
        raise RuntimeError("MLflow trace count does not match the managed evaluation dataset")
    return VariantResult(
        variant=variant,
        run_id=result.run_id,
        trace_ids=trace_ids,
        metrics=metrics,
        decision=decision,
        failed_metrics=failed_metrics,
        cases=cases,
    )


def run_comparison(
    runtime_dir: Path = DEFAULT_RUNTIME_DIR,
    results_path: Path = DEFAULT_RESULTS_PATH,
) -> dict[str, Any]:
    baseline = evaluate_variant("baseline", runtime_dir)
    governed = evaluate_variant("governed", runtime_dir)
    policy = load_release_policy()
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "dataset_sha256": sha256_file(DEFAULT_DATASET_PATH),
        "corpus_sha256": sha256_file(DEFAULT_CORPUS_PATH),
        "release_policy_sha256": sha256_file(DEFAULT_POLICY_PATH),
        "policy_version": policy.policy_version,
        "variants": {
            "baseline": baseline.to_dict(),
            "governed": governed.to_dict(),
        },
    }
    for variant in ("baseline", "governed"):
        expected = policy.expected_decisions[variant]
        observed = cast(dict[str, Any], payload["variants"])[variant]["decision"]
        if observed != expected:
            raise RuntimeError(
                f"unexpected {variant} decision: expected {expected}, observed {observed}"
            )
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def search_variant_traces(runtime_dir: Path, variant: Variant) -> list[str]:
    experiment_id = configure_offline_tracking(runtime_dir)
    traces = mlflow.search_traces(
        locations=[experiment_id],
        filter_string=f"tags.variant = '{variant}'",
        return_type="list",
    )
    return [trace.info.trace_id for trace in traces]
