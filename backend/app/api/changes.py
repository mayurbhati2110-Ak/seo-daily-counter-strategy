from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.action import ActionRecommendation
from app.outcomes.change_service import ChangeService
from app.outcomes.registry import change_registry


router = APIRouter(
    prefix="/changes",
    tags=["changes"],
)


class CreateChangeRequest(BaseModel):
    action: ActionRecommendation
    changed_by: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


change_service = ChangeService()



@router.post("")
def create_change(request: CreateChangeRequest):
    """
    Record an approved SEO action as a ChangeRecord.

    V1 is record-only:
    this endpoint does not execute or deploy
    any production change.
    """

    try:
        change = change_service.record_change(
            action=request.action,
            changed_by=request.changed_by,
            description=request.description,
        )

        change_registry.save(change)

        return change

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc