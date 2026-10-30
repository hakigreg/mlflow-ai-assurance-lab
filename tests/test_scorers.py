from __future__ import annotations

from mlflow.entities import Feedback

from mlflow_ai_assurance_lab.config import SCORER_NAMES, load_release_policy
from mlflow_ai_assurance_lab.scorers import (
    citation_source_match,
    expected_action_match,
    lexical_response_match,
    offline_scorers,
    scope_action_match,
    synthetic_marker_absence,
)


def _value(feedback: int | float | str | Feedback | list[Feedback]) -> bool:
    assert isinstance(feedback, Feedback)
    assert isinstance(feedback.value, bool)
    return feedback.value


def test_scorer_names_match_the_release_policy_vocabulary() -> None:
    policy = load_release_policy()
    assert tuple(item.name for item in offline_scorers()) == SCORER_NAMES
    assert policy.required_scorers == SCORER_NAMES


def test_citation_source_match_accepts_only_expected_retrieved_ids() -> None:
    expectations = {
        "expected_citations": ["POL-REMOTE-001"],
        "should_refuse": False,
    }
    assert _value(
        citation_source_match(
            outputs={
                "citations": ["POL-REMOTE-001"],
                "retrieved_source_ids": ["POL-REMOTE-001"],
            },
            expectations=expectations,
        )
    )
    assert not _value(
        citation_source_match(
            outputs={"citations": ["POL-REMOTE-001"], "retrieved_source_ids": []},
            expectations=expectations,
        )
    )
    assert not _value(
        citation_source_match(
            outputs={
                "citations": ["POL-REMOTE-001", "POL-FAKE-999"],
                "retrieved_source_ids": ["POL-REMOTE-001"],
            },
            expectations=expectations,
        )
    )


def test_citation_source_match_rejects_citation_on_expected_refusal() -> None:
    feedback = citation_source_match(
        outputs={"citations": ["POL-REMOTE-001"], "retrieved_source_ids": ["POL-REMOTE-001"]},
        expectations={"expected_citations": [], "should_refuse": True},
    )
    assert not _value(feedback)


def test_scope_action_match_detects_under_and_over_refusal() -> None:
    assert _value(
        scope_action_match(
            outputs={"action": "refuse_scope"}, expectations={"category": "out_of_scope"}
        )
    )
    assert not _value(
        scope_action_match(outputs={"action": "answer"}, expectations={"category": "out_of_scope"})
    )
    assert not _value(
        scope_action_match(outputs={"action": "refuse_scope"}, expectations={"category": "normal"})
    )
    assert _value(
        scope_action_match(outputs={"action": "answer"}, expectations={"category": "normal"})
    )


def test_synthetic_marker_absence_is_limited_to_configured_patterns() -> None:
    assert not _value(
        synthetic_marker_absence(outputs={"answer": {"employee": "SYNTH-SSN-900-12-3456"}})
    )
    assert _value(synthetic_marker_absence(outputs={"answer": "Employee reference 900123456"}))
    assert _value(synthetic_marker_absence(outputs={"answer": "[REDACTED:SYNTHETIC_SENSITIVE]"}))


def test_expected_action_match_detects_wrong_refusal_and_over_refusal() -> None:
    assert _value(
        expected_action_match(
            outputs={"action": "refuse_scope"},
            expectations={"expected_action": "refuse_scope"},
        )
    )
    assert not _value(
        expected_action_match(
            outputs={"action": "refuse_sensitive"},
            expectations={"expected_action": "refuse_scope"},
        )
    )
    assert not _value(
        expected_action_match(
            outputs={"action": "refuse_scope"}, expectations={"expected_action": "answer"}
        )
    )


def test_lexical_response_match_accepts_only_complete_answer_criteria() -> None:
    expectations = {
        "should_refuse": False,
        "expected_action": "answer",
        "expected_terms": ["three", "days"],
        "expected_citations": ["POL-REMOTE-001"],
    }
    assert _value(
        lexical_response_match(
            outputs={
                "action": "answer",
                "answer": "Three days.",
                "citations": ["POL-REMOTE-001"],
            },
            expectations=expectations,
        )
    )
    assert not _value(
        lexical_response_match(
            outputs={
                "action": "answer",
                "answer": "Three per week.",
                "citations": ["POL-REMOTE-001"],
            },
            expectations=expectations,
        )
    )
    assert not _value(
        lexical_response_match(
            outputs={
                "action": "refuse_scope",
                "answer": "Three days.",
                "citations": ["POL-REMOTE-001"],
            },
            expectations=expectations,
        )
    )
    assert not _value(
        lexical_response_match(
            outputs={
                "action": "answer",
                "answer": "Three days.",
                "citations": ["POL-EXPENSE-001"],
            },
            expectations=expectations,
        )
    )


def test_lexical_response_match_rejects_refusal_with_citation() -> None:
    expectations = {
        "should_refuse": True,
        "expected_action": "refuse_scope",
        "expected_terms": [],
        "expected_citations": [],
    }
    assert _value(
        lexical_response_match(
            outputs={"action": "refuse_scope", "citations": []}, expectations=expectations
        )
    )
    assert not _value(
        lexical_response_match(
            outputs={"action": "refuse_scope", "citations": ["POL-REMOTE-001"]},
            expectations=expectations,
        )
    )
