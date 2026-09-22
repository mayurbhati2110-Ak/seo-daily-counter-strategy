import pytest

from app.models.action import ApprovalState
from app.models.hypothesis import ConfidenceComponents, Hypothesis
from app.strategy.actions import ActionStrategy
from app.strategy.priority import PriorityScorer, PriorityWeights


# ============================================================
# Action Strategy
# ============================================================


def test_ctr_hypothesis_generates_action():
    strategy = ActionStrategy()

    hypotheses = [
        Hypothesis(
            hypothesis="ctr_snippet_regression",
            evidence_for=["signal:ctr"],
            confidence_components=ConfidenceComponents(
                authority=0.8,
                coverage=0.7,
                agreement=0.9,
                recency=1.0,
            ),
            next_check=["Verify the current SERP snippet."],
        )
    ]

    actions = strategy.generate(
        incident_id="incident-001",
        hypotheses=hypotheses,
        target="https://spearmint.online/pricing",
    )

    assert len(actions) == 1

    action = actions[0]

    assert action.action_type == "review_snippet"
    assert action.target == "https://spearmint.online/pricing"
    assert action.approval_state == ApprovalState.PENDING
    assert action.confidence == "medium"
    assert action.rollback
    assert action.verification_plan
    assert action.prerequisites


def test_unknown_hypothesis_does_not_generate_action():
    strategy = ActionStrategy()

    hypotheses = [
        Hypothesis(
            hypothesis="unknown_future_hypothesis",
        )
    ]

    actions = strategy.generate(
        incident_id="incident-002",
        hypotheses=hypotheses,
        target="https://spearmint.online/pricing",
    )

    assert actions == []


def test_multiple_supported_hypotheses_generate_multiple_actions():
    strategy = ActionStrategy()

    hypotheses = [
        Hypothesis(
            hypothesis="ctr_snippet_regression",
            confidence_components=ConfidenceComponents(
                coverage=0.8
            ),
        ),
        Hypothesis(
            hypothesis="competitor_improvement",
            confidence_components=ConfidenceComponents(
                coverage=0.5
            ),
        ),
    ]

    actions = strategy.generate(
        incident_id="incident-003",
        hypotheses=hypotheses,
        target="https://spearmint.online/pricing",
    )

    assert len(actions) == 2

    assert actions[0].approval_state == ApprovalState.PENDING
    assert actions[1].approval_state == ApprovalState.PENDING

    assert actions[0].action_type == "review_snippet"
    assert actions[1].action_type == "competitor_analysis"


# ============================================================
# Priority Strategy
# ============================================================


def test_priority_score_is_reproducible():
    scorer = PriorityScorer()

    result1 = scorer.score(
        business_impact=0.9,
        search_impact=0.8,
        confidence=0.7,
        urgency=0.8,
        affected_scope=0.6,
        effort=0.2,
        risk=0.1,
    )

    result2 = scorer.score(
        business_impact=0.9,
        search_impact=0.8,
        confidence=0.7,
        urgency=0.8,
        affected_scope=0.6,
        effort=0.2,
        risk=0.1,
    )

    assert result1.score == result2.score
    assert result1.level == result2.level
    assert result1.components == result2.components
    assert result1.weights == result2.weights
    assert result1.version == "priority-v1"


def test_priority_result_exposes_components_and_weights():
    scorer = PriorityScorer()

    result = scorer.score(
        business_impact=1.0,
        search_impact=1.0,
        confidence=1.0,
        urgency=1.0,
        affected_scope=1.0,
        effort=0.0,
        risk=0.0,
    )

    assert result.score == 1.0
    assert result.level == "high"

    assert set(result.components.keys()) == {
        "business_impact",
        "search_impact",
        "confidence",
        "urgency",
        "affected_scope",
        "effort",
        "risk",
    }

    assert result.weights["business_impact"] == 0.25


def test_effort_and_risk_reduce_priority():
    scorer = PriorityScorer()

    low_cost = scorer.score(
        business_impact=0.8,
        search_impact=0.8,
        confidence=0.8,
        urgency=0.8,
        affected_scope=0.8,
        effort=0.1,
        risk=0.1,
    )

    high_cost = scorer.score(
        business_impact=0.8,
        search_impact=0.8,
        confidence=0.8,
        urgency=0.8,
        affected_scope=0.8,
        effort=0.9,
        risk=0.9,
    )

    assert low_cost.score > high_cost.score


def test_custom_priority_weights_are_supported():
    weights = PriorityWeights(
        business_impact=0.50,
        search_impact=0.10,
        confidence=0.10,
        urgency=0.10,
        affected_scope=0.10,
        effort=0.05,
        risk=0.05,
    )

    scorer = PriorityScorer(weights)

    result = scorer.score(
        business_impact=1.0,
        search_impact=0.5,
        confidence=0.5,
        urgency=0.5,
        affected_scope=0.5,
        effort=0.0,
        risk=0.0,
    )

    assert result.weights["business_impact"] == 0.50
    assert 0.0 <= result.score <= 1.0


def test_priority_component_must_be_between_zero_and_one():
    scorer = PriorityScorer()

    with pytest.raises(ValueError):
        scorer.score(
            business_impact=1.2,
            search_impact=0.5,
            confidence=0.5,
            urgency=0.5,
            affected_scope=0.5,
            effort=0.2,
            risk=0.2,
        )


def test_negative_priority_weight_is_rejected():
    with pytest.raises(ValueError):
        PriorityScorer(
            PriorityWeights(
                business_impact=-0.1,
            )
        )

