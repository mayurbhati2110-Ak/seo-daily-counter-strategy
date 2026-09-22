from pathlib import Path

from app.connectors.gsc import GSCMockConnector
from app.models.incident import IncidentStatus
from app.pipeline.correlator import IncidentCorrelator
from app.pipeline.detector import SearchPerformanceDetector
from app.pipeline.normalizer import ObservationNormalizer


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def _get_signals():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()
    detector = SearchPerformanceDetector()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw_payload)

    baseline = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d") == "2026-09-18"
    ]

    current = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d") == "2026-09-20"
    ]

    return detector.detect(
        baseline=baseline,
        current=current,
    )


def test_incident_correlator_groups_related_signals():
    signals = _get_signals()

    correlator = IncidentCorrelator()
    incidents = correlator.correlate(signals)

    assert len(incidents) == 1

    incident = incidents[0]

    assert incident.site_id == "spearmint"
    assert incident.page == "https://spearmint.online/pricing"
    assert incident.query == "seo software pricing"
    assert incident.status == IncidentStatus.NEW
    assert incident.cause_established is False

    assert len(incident.signal_ids) == 3

    assert incident.metadata["signal_count"] == 3
    assert set(incident.metadata["metrics"]) == {
        "clicks",
        "ctr",
        "position",
    }


def test_incident_contains_original_signal_ids():
    signals = _get_signals()

    correlator = IncidentCorrelator()
    incidents = correlator.correlate(signals)

    incident = incidents[0]

    signal_ids = {
        signal.signal_id
        for signal in signals
    }

    assert set(incident.signal_ids) == signal_ids