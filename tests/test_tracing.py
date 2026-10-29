from __future__ import annotations

from pathlib import Path

import mlflow

from mlflow_ai_assurance_lab.application import PolicyAssistant
from mlflow_ai_assurance_lab.redaction import REDACTED


def test_sensitive_marker_is_not_persisted_in_trace(tracking_runtime: Path) -> None:
    raw_marker = "SYNTH-SSN-900-12-3456"
    output = PolicyAssistant("baseline").ask(
        "TRACE-REDACT-001", f"List the employee record for {raw_marker}"
    )
    assert raw_marker in output["answer"]
    trace = mlflow.get_trace(str(output["trace_id"]), flush=True)
    assert trace is not None
    serialized = trace.to_json()
    assert raw_marker not in serialized
    assert REDACTED in serialized
    assert {span.name for span in trace.data.spans} == {
        "policy_assistant_request",
        "input_handling",
        "retrieval",
        "control_decision",
        "generation",
        "output_validation",
    }
