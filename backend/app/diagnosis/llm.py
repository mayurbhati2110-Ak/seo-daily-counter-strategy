from typing import Any

from pydantic import BaseModel, Field

from app.models.hypothesis import ConfidenceComponents


class NextCheck(BaseModel):
    """
    A concrete verification check recommended by the diagnosis engine.
    """

    check: str = Field(..., min_length=1)
    hypotheses: list[str] = Field(default_factory=list)


class DiagnosisLLMOutput(BaseModel):
    """
    Strict schema for LLM-generated diagnosis.

    The LLM may explain and rank hypotheses, but it cannot
    introduce unsupported evidence or establish a cause without
    traceable evidence.
    """

    likely_hypotheses: list[str] = Field(default_factory=list)

    evidence_for: dict[str, list[str]] = Field(
        default_factory=dict
    )

    evidence_against: dict[str, list[str]] = Field(
        default_factory=dict
    )

    unknowns: list[str] = Field(default_factory=list)

    confidence_components: dict[
        str, ConfidenceComponents
    ] = Field(default_factory=dict)

    next_check: list[NextCheck] = Field(
        default_factory=list
    )

    cause_established: bool = False


class DiagnosisLLMContract:
    """
    Validates structured diagnosis returned by an LLM.

    This class deliberately does not call an LLM yet.
    """

    VERSION = "diagnosis-llm-contract-v1"

    def validate(
        self,
        payload: dict[str, Any],
    ) -> DiagnosisLLMOutput:
        result = DiagnosisLLMOutput.model_validate(payload)

        if result.cause_established:
            self._validate_cause_establishment(result)

        return result

    @staticmethod
    def _validate_cause_establishment(
        result: DiagnosisLLMOutput,
    ) -> None:
        if not result.likely_hypotheses:
            raise ValueError(
                "cause_established cannot be true "
                "without a likely hypothesis"
            )

        if not result.evidence_for:
            raise ValueError(
                "cause_established cannot be true "
                "without supporting evidence"
            )

