from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.outcome import (
    OutcomeClassification,
    OutcomeMeasurement,
)
from app.outcomes.measurement import OutcomeService
from app.outcomes.registry import (
    change_registry,
    outcome_registry,
)


router = APIRouter(
    prefix="/outcomes",
    tags=["outcomes"],
)


class MeasureOutcomeRequest(BaseModel):
    metric: str
    measurement_window: str

    before_value: float | None = None
    after_value: float | None = None

    classification: OutcomeClassification

    notes: str | None = None


outcome_service = OutcomeService()


@router.post("/{change_id}/measure")
def measure_outcome(
    change_id: str,
    request: MeasureOutcomeRequest,
) -> OutcomeMeasurement:
    """
    Record the measured outcome of an existing ChangeRecord.

    V1 is record-only:
    this endpoint does not fetch metrics automatically.
    """

    change = change_registry.get(change_id)

    if change is None:
        raise HTTPException(
            status_code=404,
            detail=f"ChangeRecord not found: {change_id}",
        )

    try:
        outcome = outcome_service.measure(
            change=change,
            metric=request.metric,
            measurement_window=request.measurement_window,
            before_value=request.before_value,
            after_value=request.after_value,
            classification=request.classification,
            notes=request.notes,
        )

        outcome_registry.save(outcome)

        return outcome

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get("/change/{change_id}")
def get_change_outcomes(
    change_id: str,
) -> list[OutcomeMeasurement]:
    """
    Retrieve historical outcomes associated with a ChangeRecord.
    """

    if not change_registry.exists(change_id):
        raise HTTPException(
            status_code=404,
            detail=f"ChangeRecord not found: {change_id}",
        )

    return outcome_registry.get_by_change_id(change_id)