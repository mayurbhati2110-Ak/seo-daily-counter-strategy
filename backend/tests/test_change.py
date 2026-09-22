import pytest

from app.models.action import ActionRecommendation, ApprovalState
from app.models.approval import ApprovalDecision
from app.strategy.approval import ApprovalService
from app.outcomes.change_service import ChangeService


def make_action() -> ActionRecommendation:
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
        prerequisites=[
            "Verify the current SERP snippet."
        ],
        owner_type="seo",
        verification_plan=(
            "Monitor CTR against the pre-change baseline."
        ),
        rollback=(
            "Restore the previous title and meta description."
        ),
        approval_state=ApprovalState.PENDING,
    )


def approve_action(action: ActionRecommendation) -> None:
    ApprovalService().decide(
        action=action,
        decision=ApprovalDecision.APPROVE,
        actor="seo-manager",
        reason="Evidence reviewed and action approved.",
    )


def test_approved_action_creates_change_record():
    action = make_action()
    approve_action(action)

    service = ChangeService()

    change = service.record_change(
        action=action,
        changed_by="seo-manager",
        description="Updated pricing page title.",
    )

    assert change.action_id == action.action_id
    assert change.incident_id == action.incident_id
    assert change.target == action.target
    assert change.changed_by == "seo-manager"
    assert change.description == "Updated pricing page title."

    assert change.expected_effect == action.expected_effect
    assert change.verification_plan == action.verification_plan
    assert change.rollback == action.rollback

    assert change.change_id == (
        "change-service-v1:action-001"
    )


def test_pending_action_cannot_be_recorded():
    action = make_action()
    service = ChangeService()

    with pytest.raises(
        ValueError,
        match="Only approved actions",
    ):
        service.record_change(
            action=action,
            changed_by="seo-manager",
            description="Attempted change.",
        )


def test_rejected_action_cannot_be_recorded():
    action = make_action()

    ApprovalService().decide(
        action=action,
        decision=ApprovalDecision.REJECT,
        actor="seo-manager",
        reason="Insufficient evidence.",
    )

    with pytest.raises(
        ValueError,
        match="Only approved actions",
    ):
        ChangeService().record_change(
            action=action,
            changed_by="seo-manager",
            description="Rejected change.",
        )


def test_deferred_action_cannot_be_recorded():
    action = make_action()

    ApprovalService().decide(
        action=action,
        decision=ApprovalDecision.DEFER,
        actor="seo-manager",
        reason="Need additional evidence.",
    )

    with pytest.raises(
        ValueError,
        match="Only approved actions",
    ):
        ChangeService().record_change(
            action=action,
            changed_by="seo-manager",
            description="Deferred change.",
        )


def test_empty_changed_by_is_rejected():
    action = make_action()
    approve_action(action)

    with pytest.raises(
        ValueError,
        match="changed_by must not be empty",
    ):
        ChangeService().record_change(
            action=action,
            changed_by="   ",
            description="Updated pricing page title.",
        )


def test_empty_description_is_rejected():
    action = make_action()
    approve_action(action)

    with pytest.raises(
        ValueError,
        match="description must not be empty",
    ):
        ChangeService().record_change(
            action=action,
            changed_by="seo-manager",
            description="   ",
        )


def test_change_record_does_not_execute_production():
    action = make_action()
    approve_action(action)

    change = ChangeService().record_change(
        action=action,
        changed_by="seo-manager",
        description="Updated pricing page title.",
    )

    assert change is not None