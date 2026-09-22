from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class OutcomeClassification(str, Enum):
    HELPFUL = "helpful"
    NEUTRAL = "neutral"
    HARMFUL = "harmful"
    INCONCLUSIVE = "inconclusive"


class OutcomeMeasurement(BaseModel):
    """
    Records the measured result of a previously recorded change.

    Outcomes are historical evidence and never modify the
    original ChangeRecord.
    """

    outcome_id: str = Field(..., min_length=1)

    change_id: str = Field(..., min_length=1)
    incident_id: str = Field(..., min_length=1)

    measured_at: datetime

    classification: OutcomeClassification

    metric: str = Field(..., min_length=1)

    before_value: float | None = None
    after_value: float | None = None

    measurement_window: str = Field(..., min_length=1)

    notes: str | None = None