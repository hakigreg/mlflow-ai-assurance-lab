"""Versioned release-policy decision gate."""

from __future__ import annotations

from mlflow_ai_assurance_lab.domain import Decision, ReleasePolicy


def decide(metrics: dict[str, float], policy: ReleasePolicy) -> tuple[Decision, tuple[str, ...]]:
    missing = set(policy.required_scorers) - set(metrics)
    if missing:
        raise ValueError(f"required scorer metrics are missing: {sorted(missing)}")
    failed = tuple(
        name for name in policy.required_scorers if metrics[name] < policy.thresholds[name]
    )
    return ("FAIL", failed) if failed else ("PASS", ())
