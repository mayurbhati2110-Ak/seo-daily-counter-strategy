import pytest

from app.diagnosis.llm import (
    DiagnosisLLMContract,
)


def test_valid_llm_output():
    contract = DiagnosisLLMContract()

    payload = {
    "likely_hypotheses": [
        "ctr_snippet_regression"
    ],
    "evidence_for": {
        "ctr_snippet_regression": [
            "signal:example"
        ]
    },
    "evidence_against": {},
    "unknowns": [
        "SERP feature changes are not available."
    ],
    "confidence_components": {
        "ctr_snippet_regression": {
            "authority": 0.8,
            "coverage": 0.7,
            "agreement": 0.9,
            "recency": 1.0,
        }
    },
    "next_check": [
        {
            "check": "Check current SERP snippets.",
            "hypotheses": [
                "ctr_snippet_regression"
            ],
        }
    ],
    "cause_established": False,
}
    result = contract.validate(payload)

    assert result.cause_established is False
    assert (
        result.likely_hypotheses[0]
        == "ctr_snippet_regression"
    )


def test_malformed_output_is_rejected():
    contract = DiagnosisLLMContract()

    payload = {
        "likely_hypotheses": "not-a-list",
        "cause_established": False,
    }

    with pytest.raises(Exception):
        contract.validate(payload)


def test_cause_requires_supporting_evidence():
    contract = DiagnosisLLMContract()

    payload = {
        "likely_hypotheses": [
            "technical_availability"
        ],
        "evidence_for": {},
        "evidence_against": {},
        "unknowns": [],
        "confidence_components": {},
        "next_check": [],
        "cause_established": True,
    }

    with pytest.raises(ValueError):
        contract.validate(payload)

