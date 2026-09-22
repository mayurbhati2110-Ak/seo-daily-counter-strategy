import pytest

from app.models.change import ChangeRecord
from app.models.outcome import OutcomeClassification
from app.outcomes.measurement import OutcomeService


def make_change() -> ChangeRecord:
    return ChangeRecord(
        change_id="change-service-v1:action-001",
        action_id="action-001",
        incident_id="incident-001",
        target="https://spearmint.online/pricing",
        changed_by="seo-manager",
        changed_at="2026-09-22T10:00:00Z",
        description="Updated pricing page title.",
        expected_effect="Improve organic CTR.",
        verification_plan="Monitor CTR against the pre-change baseline.",
        rollback="Restore the previous title.",
    )


def test_helpful_outcome_is_recorded():
    change = make_change()

    outcome = OutcomeService().measure(
        change=change,
        metric="gsc_ctr",
        measurement_window="28 days",
        before_value=2.5,
        after_value=3.4,
        classification=OutcomeClassification.HELPFUL,
        notes="CTR improved after the title change.",
    )

    assert outcome.change_id == change.change_id
    assert outcome.incident_id == change.incident_id
    assert outcome.metric == "gsc_ctr"
    assert outcome.before_value == 2.5
    assert outcome.after_value == 3.4
    assert outcome.classification == OutcomeClassification.HELPFUL


def test_neutral_outcome_is_recorded():
    change = make_change()

    outcome = OutcomeService().measure(
        change=change,
        metric="gsc_clicks",
        measurement_window="28 days",
        before_value=1000,
        after_value=1002,
        classification=OutcomeClassification.NEUTRAL,
    )

    assert outcome.classification == OutcomeClassification.NEUTRAL


def test_harmful_outcome_is_recorded():
    change = make_change()

    outcome = OutcomeService().measure(
        change=change,
        metric="gsc_ctr",
        measurement_window="28 days",
        before_value=3.2,
        after_value=2.1,
        classification=OutcomeClassification.HARMFUL,
    )

    assert outcome.classification == OutcomeClassification.HARMFUL


def test_inconclusive_outcome_can_have_missing_values():
    change = make_change()

    outcome = OutcomeService().measure(
        change=change,
        metric="gsc_ctr",
        measurement_window="28 days",
        before_value=None,
        after_value=None,
        classification=OutcomeClassification.INCONCLUSIVE,
        notes="Insufficient comparable data.",
    )

    assert outcome.classification == OutcomeClassification.INCONCLUSIVE
    assert outcome.before_value is None
    assert outcome.after_value is None


def test_conclusive_outcome_requires_before_value():
    change = make_change()

    with pytest.raises(
        ValueError,
        match="before_value and after_value are required",
    ):
        OutcomeService().measure(
            change=change,
            metric="gsc_ctr",
            measurement_window="28 days",
            before_value=None,
            after_value=3.4,
            classification=OutcomeClassification.HELPFUL,
        )


def test_conclusive_outcome_requires_after_value():
    change = make_change()

    with pytest.raises(
        ValueError,
        match="before_value and after_value are required",
    ):
        OutcomeService().measure(
            change=change,
            metric="gsc_ctr",
            measurement_window="28 days",
            before_value=2.5,
            after_value=None,
            classification=OutcomeClassification.HARMFUL,
        )


def test_empty_metric_is_rejected():
    change = make_change()

    with pytest.raises(
        ValueError,
        match="metric must not be empty",
    ):
        OutcomeService().measure(
            change=change,
            metric="   ",
            measurement_window="28 days",
            before_value=2.5,
            after_value=3.4,
            classification=OutcomeClassification.HELPFUL,
        )


def test_empty_measurement_window_is_rejected():
    change = make_change()

    with pytest.raises(
        ValueError,
        match="measurement_window must not be empty",
    ):
        OutcomeService().measure(
            change=change,
            metric="gsc_ctr",
            measurement_window="   ",
            before_value=2.5,
            after_value=3.4,
            classification=OutcomeClassification.HELPFUL,
        )


def test_outcome_preserves_change_reference():
    change = make_change()

    outcome = OutcomeService().measure(
        change=change,
        metric="gsc_clicks",
        measurement_window="28 days",
        before_value=100,
        after_value=130,
        classification=OutcomeClassification.HELPFUL,
    )

    assert outcome.change_id == change.change_id
    assert outcome.incident_id == change.incident_id


def test_outcome_does_not_modify_change():
    change = make_change()

    original_description = change.description

    OutcomeService().measure(
        change=change,
        metric="gsc_ctr",
        measurement_window="28 days",
        before_value=2.5,
        after_value=3.4,
        classification=OutcomeClassification.HELPFUL,
    )

    assert change.description == original_description