from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SignalDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    CHANGE = "change"
    ANOMALY = "anomaly"


class SignalType(str, Enum):
    AVAILABILITY = "availability"
    INDEXATION = "indexation"
    SEARCH_PERFORMANCE = "search_performance"
    RANK = "rank"
    CANNIBALIZATION = "cannibalization"
    TECHNICAL_HEALTH = "technical_health"
    CORE_WEB_VITALS = "core_web_vitals"
    BUSINESS_IMPACT = "business_impact"
    COMPETITOR_CHANGE = "competitor_change"
    OFF_PAGE = "off_page"
    AI_GEO = "ai_geo"


class Signal(BaseModel):
    signal_id: str = Field(..., min_length=1)
    site_id: str = Field(..., min_length=1)

    signal_type: SignalType
    direction: SignalDirection

    metric: str
    current_value: float | int | None = None
    baseline_value: float | int | None = None
    change_percent: float | None = None

    target: str | None = None
    url: str | None = None
    query: str | None = None

    detected_at: datetime
    observation_ids: list[str] = Field(default_factory=list)

    detector_version: str = Field(..., min_length=1)

    metadata: dict = Field(default_factory=dict)