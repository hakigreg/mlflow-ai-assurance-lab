from __future__ import annotations

from mlflow.entities import Feedback

from mlflow_ai_assurance_lab.scorers import (
    citation_validity,
    groundedness_proxy,
    refusal_behavior,
)


def test_citation_validity_rejects_unknown_source() -> None:
    feedback = citation_validity(
        outputs={"citations": ["POL-FAKE-999"], "retrieved_source_ids": ["POL-REMOTE-001"]},
        expectations={
            "expected_citations": ["POL-REMOTE-001"],
            "should_refuse": False,
        },
    )
    assert isinstance(feedback, Feedback)
    assert feedback.value is False


def test_refusal_behavior_requires_expected_action() -> None:
    feedback = refusal_behavior(
        outputs={"action": "answer"},
        expectations={"expected_action": "refuse_scope"},
    )
    assert isinstance(feedback, Feedback)
    assert feedback.value is False


def test_groundedness_proxy_is_limited_and_deterministic() -> None:
    feedback = groundedness_proxy(
        outputs={"action": "answer", "answer": "Three days.", "citations": ["POL-REMOTE-001"]},
        expectations={
            "should_refuse": False,
            "expected_terms": ["three", "days"],
            "expected_citations": ["POL-REMOTE-001"],
        },
    )
    assert isinstance(feedback, Feedback)
    assert feedback.value is True
    assert "limited deterministic proxy" in (feedback.rationale or "")
