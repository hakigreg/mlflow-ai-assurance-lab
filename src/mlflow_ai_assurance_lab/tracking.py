"""Local-only MLflow tracking and managed evaluation dataset setup."""

from __future__ import annotations

import os
from pathlib import Path

import mlflow
from mlflow.genai.datasets import EvaluationDataset, create_dataset, search_datasets

from mlflow_ai_assurance_lab.config import load_evaluation_records

EXPERIMENT_NAME = "mlflow-ai-assurance-lab-offline"
DATASET_NAME = "synthetic-policy-assurance-v1"


def configure_offline_tracking(runtime_dir: Path) -> str:
    runtime_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir = runtime_dir / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")
    os.environ.setdefault("MLFLOW_ENABLE_TELEMETRY", "false")
    os.environ.setdefault("DO_NOT_TRACK", "1")
    os.environ.setdefault("MLFLOW_GENAI_EVAL_MAX_WORKERS", "1")
    os.environ.setdefault("MLFLOW_GENAI_EVAL_SKIP_TRACE_VALIDATION", "true")
    tracking_uri = f"sqlite:///{(runtime_dir / 'mlflow.db').resolve()}"
    mlflow.set_tracking_uri(tracking_uri)
    experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = mlflow.create_experiment(
            EXPERIMENT_NAME, artifact_location=artifact_dir.resolve().as_uri()
        )
    else:
        experiment_id = experiment.experiment_id
    mlflow.set_experiment(experiment_id=experiment_id)
    return experiment_id


def managed_dataset(experiment_id: str) -> EvaluationDataset:
    matches = search_datasets(
        experiment_ids=[experiment_id],
        filter_string=f"name = '{DATASET_NAME}'",
        max_results=2,
    )
    if len(matches) > 1:
        raise RuntimeError(f"multiple managed datasets named {DATASET_NAME!r}")
    if matches:
        dataset = matches[0]
    else:
        dataset = create_dataset(
            name=DATASET_NAME,
            experiment_id=[experiment_id],
            tags={
                "dataset_version": "policy-assurance-v1",
                "dataset_schema_version": "1.1",
                "content": "synthetic-publishable-only",
            },
        )
    dataset.merge_records(load_evaluation_records())
    return dataset
