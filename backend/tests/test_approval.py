from datetime import datetime

import pytest

from app.models.action import ActionRecommendation, ApprovalState
from app.models.approval import ApprovalDecision
from app.strategy.approval import ApprovalService


def make_action():
    return ActionRecommendation(
        action_id="action-001",
        incident_id="incident-001",
        action_type="review_snippet",
        target="https://spearmint.online/pricing",
        why_now="CTR regression detected.",
        expected_effect="Improve organic CTR.",
        confidence="medium",
        business_value="Recover qualified organic traffic.",
        effort="low",
        risk="low",
        prerequisites=["Verify the current SERP snippet."],
        owner_type="seo",
        verification_plan="Monitor CTR against the pre-change baseline.",
        rollback="Restore the previous title and meta description.",
        approval_state=ApprovalState.PENDING,
    )


def test_approve_action_creates_audit_record():
    service = ApprovalService()
    action = make_action()

    record = service.decide(
        action=action,
        decision=ApprovalDecision.APPROVE,
        actor="seo-manager",
        reason="Evidence reviewed and action approved.",
    )

    assert record.action_id == action.action_id
    assert record.incident_id == action.incident_id
    assert record.decision == ApprovalDecision.APPROVE
    assert record.actor == "seo-manager"
    assert record.target == action.target
    assert record.reason == "Evidence reviewed and action approved."
    assert isinstance(record.decided_at, datetime)
    assert action.approval_state == ApprovalState.APPROVED


def test_reject_and_defer_update_action_state():
    service = ApprovalService()

    rejected_action = make_action()
    rejected = service.decide(
        rejected_action,
        ApprovalDecision.REJECT,
        "seo-manager",
        "Insufficient evidence.",
    )

    assert rejected.decision == ApprovalDecision.REJECT
    assert rejected_action.approval_state == ApprovalState.REJECTED

    deferred_action = make_action()
    deferred = service.decide(
        deferred_action,
        ApprovalDecision.DEFER,
        "seo-manager",
        "Need additional evidence.",
    )

    assert deferred.decision == ApprovalDecision.DEFER
    assert deferred_action.approval_state == ApprovalState.DEFERRED


def test_non_pending_action_cannot_be_decided_again():
    service = ApprovalService()
    action = make_action()

    service.decide(
        action,
        ApprovalDecision.APPROVE,
        "seo-manager",
    )

    with pytest.raises(ValueError, match="Only pending actions"):
        service.decide(
            action,
            ApprovalDecision.REJECT,
            "another-user",
        )


def test_empty_actor_is_rejected():
    service = ApprovalService()
    action = make_action()

    with pytest.raises(ValueError, match="actor must not be empty"):
        service.decide(
            action,
            ApprovalDecision.APPROVE,
            "   ",
        )


def test_approval_does_not_execute_production_changes():
    service = ApprovalService()
    action = make_action()

    record = service.decide(
        action,
        ApprovalDecision.APPROVE,
        "seo-manager",
    )

    assert record.metadata["production_execution"] is False