from pydantic import BaseModel, Field


class ConfidenceComponents(BaseModel):
    authority: float = 0.0
    coverage: float = 0.0
    agreement: float = 0.0
    recency: float = 0.0


class Hypothesis(BaseModel):
    hypothesis: str = Field(..., min_length=1)

    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)

    confidence_components: ConfidenceComponents = Field(
        default_factory=ConfidenceComponents
    )

    next_check: list[str] = Field(default_factory=list)