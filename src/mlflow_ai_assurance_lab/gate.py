"""Versioned release-policy decision gate."""

from __future__ import annotations

import math
from typing import Any, cast

from mlflow_ai_assurance_lab.domain import Decision, ReleasePolicy


class GateInputError(ValueError):
    """Raised when metrics or recorded results cannot be safely gated."""


def decide(metrics: dict[str, float], policy: ReleasePolicy) -> tuple[Decision, tuple[str, ...]]:
    missing = set(policy.required_scorers) - set(metrics)
    if missing:
        raise GateInputError(f"required scorer metrics are missing: {sorted(missing)}")
    unexpected = set(metrics) - set(policy.required_scorers)
    if unexpected:
        raise GateInputError(f"unexpected scorer metrics are present: {sorted(unexpected)}")
    for name in policy.required_scorers:
        value = metrics[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise GateInputError(f"metric {name!r} must be a number")
        if not math.isfinite(value) or value < 0.0 or value > 1.0:
            raise GateInputError(
                f"metric {name!r} must be finite and in the inclusive range [0, 1]"
            )
    failed = tuple(
        name for name in policy.required_scorers if metrics[name] < policy.thresholds[name]
    )
    return ("FAIL", failed) if failed else ("PASS", ())


def assess_recorded_results(
    results: dict[str, Any],
    variant: str,
    policy: ReleasePolicy,
    policy_digest: str,
) -> tuple[Decision, tuple[str, ...]]:
    """Validate a recorded result envelope and independently recompute its decision."""

    if results.get("schema_version") != "1.0":
        raise GateInputError("evaluation results use an unsupported schema_version")
    if results.get("policy_version") != policy.policy_version:
        raise GateInputError("evaluation results policy_version does not match the release policy")
    if results.get("release_policy_sha256") != policy_digest:
        raise GateInputError("evaluation results release_policy_sha256 is stale or inconsistent")
    variants = results.get("variants")
    if not isinstance(variants, dict) or variant not in variants:
        raise GateInputError(f"evaluation results are missing variant {variant!r}")
    variant_result = variants[variant]
    if not isinstance(variant_result, dict):
        raise GateInputError(f"evaluation result for {variant!r} must be an object")
    if variant_result.get("variant") != variant:
        raise GateInputError(f"recorded variant identity does not match {variant!r}")
    raw_metrics = variant_result.get("metrics")
    if not isinstance(raw_metrics, dict) or not all(isinstance(key, str) for key in raw_metrics):
        raise GateInputError(f"recorded metrics for {variant!r} must be an object")
    metrics = cast(dict[str, float], raw_metrics)
    decision, failed = decide(metrics, policy)
    recorded_decision = variant_result.get("decision")
    recorded_failed = variant_result.get("failed_metrics")
    if recorded_decision != decision:
        raise GateInputError(
            f"recorded decision {recorded_decision!r} does not match recomputed {decision!r}"
        )
    if recorded_failed != list(failed):
        raise GateInputError("recorded failed_metrics do not match the recomputed gate result")
    return decision, failed
