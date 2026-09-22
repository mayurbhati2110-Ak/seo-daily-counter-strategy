from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IncidentStatus(str, Enum):
    NEW = "NEW"
    CONFIRMED = "CONFIRMED"
    DIAGNOSING = "DIAGNOSING"
    ACTION_PROPOSED = "ACTION_PROPOSED"
    APPROVED = "APPROVED"
    SHIPPED = "SHIPPED"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    REGRESSED = "REGRESSED"


class Incident(BaseModel):
    incident_id: str = Field(..., min_length=1)
    site_id: str = Field(..., min_length=1)

    status: IncidentStatus = IncidentStatus.NEW

    target: str | None = None
    page: str | None = None
    query: str | None = None
    topic: str | None = None

    started_at: datetime
    detected_at: datetime

    signal_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

    cause_established: bool = False

    metadata: dict = Field(default_factory=dict)