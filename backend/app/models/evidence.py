from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceRole(str, Enum):
    SUPPORTING = "supporting"
    CONTRADICTING = "contradicting"
    CONTEXT = "context"


class EvidenceItem(BaseModel):
    evidence_id: str = Field(..., min_length=1)
    source: str
    source_tier: str
    fact: str
    metric: str | None = None
    value: Any = None
    observed_at: datetime
    retrieved_at: datetime
    freshness_status: str
    role: EvidenceRole = EvidenceRole.CONTEXT
    provenance: dict[str, Any] = Field(default_factory=dict)


class EvidencePacket(BaseModel):
    incident_id: str = Field(..., min_length=1)
    status: str
    target: str | None = None
    window_start: datetime
    window_end: datetime

    signal_ids: list[str] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)

    contradictions: list[str] = Field(default_factory=list)
    missing_checks: list[str] = Field(default_factory=list)
    recent_changes: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)

    detector_versions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)