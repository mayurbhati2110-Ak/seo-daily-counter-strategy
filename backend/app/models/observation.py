from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SourceTier(str, Enum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"


class DataStatus(str, Enum):
    VALID = "valid"
    STALE = "stale"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class Observation(BaseModel):
    observation_id: str = Field(..., min_length=1)
    site_id: str = Field(..., min_length=1)

    source: str = Field(..., min_length=1)
    source_tier: SourceTier

    metric: str = Field(..., min_length=1)
    value: float | int | str | bool | None = None

    observed_at: datetime
    retrieved_at: datetime

    status: DataStatus = DataStatus.VALID

    url: str | None = None
    query: str | None = None
    country: str | None = None
    language: str | None = None
    device: str | None = None

    unit: str | None = None

    provenance: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)