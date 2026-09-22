from datetime import datetime, timezone

from app.models.change import ChangeRecord
from app.models.outcome import (
    OutcomeClassification,
    OutcomeMeasurement,
)


class OutcomeService:
    """
    Records and classifies the measured outcome of a ChangeRecord.

    V1 is record-only. This service does not fetch metrics itself.
    The caller supplies the measured before/after values.
    """

    VERSION = "outcome-service-v1"

    def measure(
        self,
        change: ChangeRecord,
        metric: str,
        measurement_window: str,
        before_value: float | None,
        after_value: float | None,
        classification: OutcomeClassification,
        notes: str | None = None,
    ) -> OutcomeMeasurement:
        """
        Create an OutcomeMeasurement for an existing ChangeRecord.
        """

        if not metric.strip():
            raise ValueError("metric must not be empty")

        if not measurement_window.strip():
            raise ValueError(
                "measurement_window must not be empty"
            )

        if (
            classification != OutcomeClassification.INCONCLUSIVE
            and (
                before_value is None
                or after_value is None
            )
        ):
            raise ValueError(
                "before_value and after_value are required "
                "for a conclusive outcome."
            )

        outcome_id = (
            f"{self.VERSION}:"
            f"{change.change_id}:"
            f"{metric}"
        )

        return OutcomeMeasurement(
            outcome_id=outcome_id,
            change_id=change.change_id,
            incident_id=change.incident_id,
            measured_at=datetime.now(timezone.utc),
            classification=classification,
            metric=metric,
            before_value=before_value,
            after_value=after_value,
            measurement_window=measurement_window,
            notes=notes,
        )