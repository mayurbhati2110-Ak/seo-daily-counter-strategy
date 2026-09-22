from enum import Enum

from pydantic import BaseModel, Field


class ApprovalState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


class ActionRecommendation(BaseModel):
    action_id: str = Field(..., min_length=1)

    incident_id: str
    action_type: str

    target: str

    why_now: str
    expected_effect: str

    confidence: str
    business_value: str
    effort: str
    risk: str

    prerequisites: list[str] = Field(default_factory=list)

    owner_type: str

    verification_plan: str
    rollback: str

    approval_state: ApprovalState = ApprovalState.PENDING