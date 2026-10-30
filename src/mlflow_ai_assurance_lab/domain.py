"""Typed contracts shared by the application and assurance workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

Variant = Literal["baseline", "governed"]
Decision = Literal["PASS", "FAIL"]


@dataclass(frozen=True)
class PolicyDocument:
    document_id: str
    title: str
    topics: tuple[str, ...]
    content: str
    trusted: bool = True


@dataclass(frozen=True)
class RetrievedDocument:
    document: PolicyDocument
    score: int


@dataclass(frozen=True)
class AssistantResponse:
    case_id: str
    variant: Variant
    action: str
    answer: str
    citations: tuple[str, ...]
    retrieved_source_ids: tuple[str, ...]
    trace_id: str
    prompt_version: str
    provider: str

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["citations"] = list(self.citations)
        value["retrieved_source_ids"] = list(self.retrieved_source_ids)
        return value


@dataclass(frozen=True)
class ReleasePolicy:
    schema_version: str
    policy_version: str
    required_scorers: tuple[str, ...]
    thresholds: dict[str, float]
    expected_decisions: dict[Variant, Decision]


@dataclass(frozen=True)
class VariantResult:
    variant: Variant
    run_id: str
    trace_ids: tuple[str, ...]
    metrics: dict[str, float]
    decision: Decision
    failed_metrics: tuple[str, ...]
    persistence_safe: bool
    cases: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "run_id": self.run_id,
            "trace_ids": list(self.trace_ids),
            "metrics": self.metrics,
            "decision": self.decision,
            "failed_metrics": list(self.failed_metrics),
            "persistence_safe": self.persistence_safe,
            "cases": list(self.cases),
        }
