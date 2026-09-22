from app.models.outcome import OutcomeMeasurement


class OutcomeRegistry:
    """
    V1 in-memory registry for historical OutcomeMeasurements.

    This allows previously measured outcomes to be retrieved as
    historical evidence.

    Persistent storage will be introduced later.
    """

    def __init__(self) -> None:
        self._outcomes: dict[str, OutcomeMeasurement] = {}

    def save(
        self,
        outcome: OutcomeMeasurement,
    ) -> OutcomeMeasurement:
        self._outcomes[outcome.outcome_id] = outcome
        return outcome

    def get(
        self,
        outcome_id: str,
    ) -> OutcomeMeasurement | None:
        return self._outcomes.get(outcome_id)

    def get_by_change_id(
        self,
        change_id: str,
    ) -> list[OutcomeMeasurement]:
        return [
            outcome
            for outcome in self._outcomes.values()
            if outcome.change_id == change_id
        ]

    def get_by_incident_id(
        self,
        incident_id: str,
    ) -> list[OutcomeMeasurement]:
        return [
            outcome
            for outcome in self._outcomes.values()
            if outcome.incident_id == incident_id
        ]

    def clear(self) -> None:
        self._outcomes.clear()