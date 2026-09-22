from datetime import datetime, timezone

from app.models.action import ActionRecommendation, ApprovalState
from app.models.change import ChangeRecord


class ChangeService:
    """
    Records an actual change associated with an approved action.

    V1 is record-only:
    this service does not execute, deploy, or modify
    anything in a production system.
    """

    VERSION = "change-service-v1"

    def record_change(
        self,
        action: ActionRecommendation,
        changed_by: str,
        description: str,
    ) -> ChangeRecord:
        """
        Create a ChangeRecord for an approved action.

        Only APPROVED actions can become recorded changes.
        """

        if action.approval_state != ApprovalState.APPROVED:
            raise ValueError(
                "Only approved actions can be recorded as changes."
            )

        if not changed_by.strip():
            raise ValueError("changed_by must not be empty")

        if not description.strip():
            raise ValueError("description must not be empty")

        return ChangeRecord(
            change_id=f"{self.VERSION}:{action.action_id}",
            action_id=action.action_id,
            incident_id=action.incident_id,
            target=action.target,
            changed_by=changed_by,
            changed_at=datetime.now(timezone.utc),
            description=description,
            expected_effect=action.expected_effect,
            verification_plan=action.verification_plan,
            rollback=action.rollback,
        )