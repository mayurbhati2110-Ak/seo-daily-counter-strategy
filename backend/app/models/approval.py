from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"


class ApprovalRecord(BaseModel):
    """
    Records the explicit human decision on an action recommendation.

    V1 is read-only from the production-system perspective:
    recording an approval does not execute the action.
    """

    approval_id: str = Field(..., min_length=1)
    action_id: str = Field(..., min_length=1)
    incident_id: str = Field(..., min_length=1)

    decision: ApprovalDecision

    actor: str = Field(..., min_length=1)
    decided_at: datetime

    target: str | None = None
    reason: str | None = None

    metadata: dict = Field(default_factory=dict)