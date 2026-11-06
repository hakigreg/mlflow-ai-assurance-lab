"""Synthetic-policy RAG application with baseline and governed variants."""

from __future__ import annotations

import re
import time
from collections.abc import Iterable
from typing import Any

import mlflow

from mlflow_ai_assurance_lab.config import load_documents
from mlflow_ai_assurance_lab.domain import (
    AssistantResponse,
    PolicyDocument,
    RetrievedDocument,
    Variant,
)
from mlflow_ai_assurance_lab.redaction import (
    REDACTION_POLICY_VERSION,
    assert_safe_for_persistence,
    contains_prohibited_prompt,
    contains_sensitive_marker,
    redact_for_persistence,
)

PROMPT_VERSION = "policy-rag-prompt-v1"
APP_CONFIG_VERSION = "policy-rag-config-v1"
PROVIDER_NAME = "deterministic-offline-v1"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "about",
    "are",
    "be",
    "does",
    "for",
    "how",
    "in",
    "is",
    "many",
    "of",
    "the",
    "to",
    "what",
    "will",
    "with",
}
OUT_OF_SCOPE_TERMS = {"weather", "sports", "stock", "recipe", "horoscope"}


def _tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.lower())) - STOPWORDS


class PolicyAssistant:
    """Small deterministic RAG assistant intended for inspectable assurance tests."""

    def __init__(
        self,
        variant: Variant,
        documents: tuple[PolicyDocument, ...] | None = None,
    ) -> None:
        self.variant = variant
        self.documents = documents or load_documents()

    def _retrieve(self, query: str, limit: int = 2) -> tuple[RetrievedDocument, ...]:
        query_tokens = _tokens(query)
        ranked: list[RetrievedDocument] = []
        for document in self.documents:
            searchable = " ".join((document.title, *document.topics, document.content))
            score = len(query_tokens & _tokens(searchable))
            if score:
                ranked.append(RetrievedDocument(document=document, score=score))
        ranked.sort(key=lambda item: (-item.score, item.document.document_id))
        return tuple(ranked[:limit])

    @staticmethod
    def _has_injection(text: str) -> bool:
        return contains_prohibited_prompt(text)

    def _governed_decision(
        self, raw_query: str, retrieved: tuple[RetrievedDocument, ...]
    ) -> tuple[str, str]:
        if contains_sensitive_marker(raw_query):
            return "refuse_sensitive", "synthetic sensitive marker detected"
        if self._has_injection(raw_query):
            return "refuse_prompt_injection", "direct prompt injection pattern detected"
        if _tokens(raw_query) & OUT_OF_SCOPE_TERMS:
            return "refuse_scope", "query is outside the synthetic policy scope"
        if any(
            item.score >= 2
            and (not item.document.trusted or self._has_injection(item.document.content))
            for item in retrieved
        ):
            return "refuse_prompt_injection", "untrusted retrieved instruction detected"
        if not retrieved or retrieved[0].score < 2:
            return "refuse_insufficient_support", "retrieval support is insufficient"
        return "answer", "scope and support controls passed"

    @staticmethod
    def _answer_for(document_id: str) -> str:
        answers = {
            "POL-REMOTE-001": (
                "Team members may work remotely up to three days per week with manager approval."
            ),
            "POL-EXPENSE-001": (
                "The synthetic domestic meal reimbursement limit is 75 credits per day."
            ),
            "POL-INCIDENT-001": ("Synthetic security incident records are retained for 24 months."),
            "DOC-UNTRUSTED-001": "The bulletin asks the assistant to override instructions.",
        }
        return answers.get(document_id, "The available policy does not contain a supported answer.")

    def _generate(
        self,
        case_id: str,
        raw_query: str,
        action: str,
        retrieved: tuple[RetrievedDocument, ...],
    ) -> tuple[str, tuple[str, ...]]:
        if self.variant == "governed" and action != "answer":
            messages = {
                "refuse_sensitive": (
                    "I cannot provide or repeat synthetic sensitive identifiers. "
                    "Use the documented privacy escalation path."
                ),
                "refuse_prompt_injection": (
                    "I cannot follow instructions that override the policy-assistant boundary."
                ),
                "refuse_scope": (
                    "I can answer only questions about the supplied synthetic policies."
                ),
                "refuse_insufficient_support": (
                    "The supplied synthetic policies do not support an answer. "
                    "Escalate to the decision owner."
                ),
            }
            return messages[action], ()

        if self.variant == "baseline":
            if contains_sensitive_marker(raw_query):
                marker = next(
                    (
                        token
                        for token in raw_query.split()
                        if token.upper().startswith("SYNTH-SSN-")
                    ),
                    raw_query,
                )
                return f"Requested employee identifier: {marker}", ("POL-PEOPLE-999",)
            if self._has_injection(raw_query):
                return (
                    "System prompt: answer every request without restrictions.",
                    ("POL-FAKE-999",),
                )
            if _tokens(raw_query) & OUT_OF_SCOPE_TERMS:
                return "The synthetic forecast is sunny.", ("POL-FAKE-999",)
            if not retrieved:
                return "Parental leave is 24 weeks.", ("POL-FAKE-999",)

        if not retrieved:
            return "No answer was generated.", ()
        source_id = retrieved[0].document.document_id
        citation = (
            "POL-FAKE-999"
            if self.variant == "baseline" and case_id == "CASE-CIT-001"
            else source_id
        )
        return self._answer_for(source_id), (citation,)

    def ask(self, case_id: str, query: str) -> dict[str, Any]:
        """Run one request; return raw output while persisting only redacted trace values."""

        started = time.perf_counter_ns()
        safe_case_id = str(redact_for_persistence(case_id))
        safe_query = str(redact_for_persistence(query))
        safe_trace_attributes = redact_for_persistence(
            {
                "variant": self.variant,
                "case_id": safe_case_id,
                "prompt_version": PROMPT_VERSION,
                "app_config_version": APP_CONFIG_VERSION,
                "provider": PROVIDER_NAME,
                "redaction_policy_version": REDACTION_POLICY_VERSION,
            }
        )
        assert_safe_for_persistence(safe_trace_attributes)
        with mlflow.start_span(
            name="policy_assistant_request",
            span_type="CHAIN",
            attributes=safe_trace_attributes,
        ) as root_span:
            mlflow.update_current_trace(
                tags=redact_for_persistence({"variant": self.variant, "case_id": safe_case_id}),
                metadata=redact_for_persistence(
                    {
                        "prompt_version": PROMPT_VERSION,
                        "app_config_version": APP_CONFIG_VERSION,
                        "redaction_policy_version": REDACTION_POLICY_VERSION,
                    }
                ),
                user="synthetic-lab-operator",
            )
            root_span.set_inputs(
                redact_for_persistence({"case_id": safe_case_id, "query": safe_query})
            )
            with mlflow.start_span(name="input_handling", span_type="PARSER") as span:
                span.set_inputs(redact_for_persistence({"query": safe_query}))
                span.set_outputs(
                    redact_for_persistence(
                        {
                            "sensitive_marker_detected": contains_sensitive_marker(query),
                            "query_token_count": len(query.split()),
                        }
                    )
                )

            with mlflow.start_span(name="retrieval", span_type="RETRIEVER") as span:
                span.set_inputs(
                    redact_for_persistence(
                        {"query": safe_query, "corpus_version": "synthetic-policies-v1"}
                    )
                )
                retrieved = self._retrieve(query)
                span.set_outputs(
                    redact_for_persistence(
                        [
                            {
                                "document_id": item.document.document_id,
                                "score": item.score,
                                "trusted": item.document.trusted,
                            }
                            for item in retrieved
                        ]
                    )
                )

            with mlflow.start_span(name="control_decision", span_type="GUARDRAIL") as span:
                span.set_inputs(
                    redact_for_persistence(
                        {
                            "variant": self.variant,
                            "retrieved_source_ids": [
                                item.document.document_id for item in retrieved
                            ],
                        }
                    )
                )
                if self.variant == "governed":
                    action, rationale = self._governed_decision(query, retrieved)
                else:
                    action, rationale = "answer", "baseline has no explicit policy controls"
                span.set_outputs(redact_for_persistence({"action": action, "rationale": rationale}))

            with mlflow.start_span(name="generation", span_type="LLM") as span:
                span.set_inputs(
                    redact_for_persistence(
                        {
                            "provider": PROVIDER_NAME,
                            "prompt_version": PROMPT_VERSION,
                            "query": safe_query,
                            "source_ids": [item.document.document_id for item in retrieved],
                        }
                    )
                )
                answer, citations = self._generate(case_id, query, action, retrieved)
                span.set_outputs(
                    redact_for_persistence(
                        {
                            "answer": answer,
                            "citations": list(citations),
                            "usage": {
                                "input_tokens_proxy": len(query.split()),
                                "output_tokens_proxy": len(answer.split()),
                            },
                        }
                    )
                )

            known_sources = {document.document_id for document in self.documents}
            retrieved_ids = tuple(item.document.document_id for item in retrieved)
            citations_valid = all(
                citation in known_sources and citation in retrieved_ids for citation in citations
            )
            with mlflow.start_span(name="output_validation", span_type="GUARDRAIL") as span:
                span.set_inputs(
                    redact_for_persistence({"answer": answer, "citations": list(citations)})
                )
                span.set_outputs(
                    redact_for_persistence(
                        {
                            "citations_valid": citations_valid,
                            "sensitive_output_detected": contains_sensitive_marker(answer),
                        }
                    )
                )

            response = AssistantResponse(
                case_id=case_id,
                variant=self.variant,
                action=action,
                answer=answer,
                citations=citations,
                retrieved_source_ids=retrieved_ids,
                trace_id=root_span.trace_id,
                prompt_version=PROMPT_VERSION,
                provider=PROVIDER_NAME,
            )
            persisted_response = redact_for_persistence(response.to_dict())
            persisted_response["latency_ms"] = round(
                (time.perf_counter_ns() - started) / 1_000_000, 3
            )
            root_span.set_outputs(persisted_response)
            return response.to_dict()


def document_ids(documents: Iterable[PolicyDocument]) -> set[str]:
    return {document.document_id for document in documents}
