from pathlib import Path

from app.connectors.gsc import GSCMockConnector
from app.diagnosis.evidence import EvidenceEngine
from app.models.observation import Observation
from app.pipeline.correlator import IncidentCorrelator
from app.pipeline.detector import SearchPerformanceDetector
from app.pipeline.normalizer import ObservationNormalizer


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def _get_pipeline_data():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw_payload)

    baseline = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d")
        == "2026-09-18"
    ]

    current = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d")
        == "2026-09-20"
    ]

    detector = SearchPerformanceDetector()

    signals = detector.detect(
        baseline,
        current,
    )

    correlator = IncidentCorrelator()

    incidents = correlator.correlate(signals)

    return observations, signals, incidents


def test_evidence_engine_builds_packet():
    observations, signals, incidents = _get_pipeline_data()

    assert len(incidents) == 1

    incident = incidents[0]

    incident_signals = [
        signal
        for signal in signals
        if signal.signal_id in incident.signal_ids
    ]

    incident_observations = [
        observation
        for observation in observations
        if observation.url == incident.page
        and observation.query == incident.query
    ]

    engine = EvidenceEngine()

    packet = engine.build_packet(
        incident=incident,
        signals=incident_signals,
        observations=incident_observations,
    )

    assert packet.incident_id == incident.incident_id
    assert packet.status == "NEW"
    assert packet.target == "https://spearmint.online/pricing"

    assert len(packet.signal_ids) == 3
    assert len(packet.evidence_items) == 11

    assert packet.detector_versions == [
        "search-performance-v1"
    ]


def test_evidence_items_are_traceable():
    observations, signals, incidents = _get_pipeline_data()

    incident = incidents[0]

    incident_signals = [
        signal
        for signal in signals
        if signal.signal_id in incident.signal_ids
    ]

    incident_observations = [
        observation
        for observation in observations
        if observation.url == incident.page
        and observation.query == incident.query
    ]

    engine = EvidenceEngine()

    packet = engine.build_packet(
        incident,
        incident_signals,
        incident_observations,
    )

    evidence_ids = {
        item.evidence_id
        for item in packet.evidence_items
    }

    for signal in incident_signals:
        assert (
            f"signal:{signal.signal_id}"
            in evidence_ids
        )

    for observation in incident_observations:
        assert (
            f"observation:{observation.observation_id}"
            in evidence_ids
        )


def test_evidence_packet_does_not_establish_cause():
    observations, signals, incidents = _get_pipeline_data()

    incident = incidents[0]

    incident_signals = [
        signal
        for signal in signals
        if signal.signal_id in incident.signal_ids
    ]

    engine = EvidenceEngine()

    packet = engine.build_packet(
        incident=incident,
        signals=incident_signals,
        observations=observations,
    )

    assert packet.metadata["cause_established"] is False
    assert packet.contradictions == []
    assert packet.missing_checks == []