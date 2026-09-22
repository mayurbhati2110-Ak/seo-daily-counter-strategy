from datetime import datetime, timezone

from app.models.action import ActionRecommendation, ApprovalState
from app.models.approval import ApprovalDecision, ApprovalRecord


class ApprovalService:
    """
    Handles human approval decisions for action recommendations.

    V1 records the decision only.
    It does not execute or modify anything in a production system.
    """

    VERSION = "approval-service-v1"

    def decide(
        self,
        action: ActionRecommendation,
        decision: ApprovalDecision,
        actor: str,
        reason: str | None = None,
    ) -> ApprovalRecord:
        if not actor.strip():
            raise ValueError("actor must not be empty")

        self._validate_transition(action, decision)

        action.approval_state = self._map_state(decision)

        return ApprovalRecord(
            approval_id=f"{self.VERSION}:{action.action_id}",
            action_id=action.action_id,
            incident_id=action.incident_id,
            decision=decision,
            actor=actor,
            decided_at=datetime.now(timezone.utc),
            target=action.target,
            reason=reason,
            metadata={
                "service_version": self.VERSION,
                "production_execution": False,
            },
        )

    @staticmethod
    def _map_state(decision: ApprovalDecision) -> ApprovalState:
        mapping = {
            ApprovalDecision.APPROVE: ApprovalState.APPROVED,
            ApprovalDecision.REJECT: ApprovalState.REJECTED,
            ApprovalDecision.DEFER: ApprovalState.DEFERRED,
        }

        return mapping[decision]

    @staticmethod
    def _validate_transition(
        action: ActionRecommendation,
        decision: ApprovalDecision,
    ) -> None:
        if action.approval_state != ApprovalState.PENDING:
            raise ValueError(
                "Only pending actions can receive an approval decision."
            )