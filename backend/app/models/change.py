from datetime import datetime

from pydantic import BaseModel, Field


class ChangeRecord(BaseModel):
    """
    Records an actual change associated with an approved SEO action.

    V1 is record-only:
    this model does not execute or deploy any production change.
    """

    change_id: str = Field(..., min_length=1)

    action_id: str = Field(..., min_length=1)
    incident_id: str = Field(..., min_length=1)

    target: str = Field(..., min_length=1)

    changed_by: str = Field(..., min_length=1)
    changed_at: datetime

    description: str = Field(..., min_length=1)

    expected_effect: str = Field(..., min_length=1)
    verification_plan: str = Field(..., min_length=1)
    rollback: str = Field(..., min_length=1)