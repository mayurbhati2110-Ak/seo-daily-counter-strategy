from pathlib import Path

from app.connectors.gsc import GSCMockConnector
from app.diagnosis.evidence import EvidenceEngine
from app.diagnosis.engine import DiagnosisEngine
from app.models.observation import Observation
from app.pipeline.correlator import IncidentCorrelator
from app.pipeline.detector import SearchPerformanceDetector
from app.pipeline.normalizer import ObservationNormalizer


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def _get_evidence_packet():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(
        raw_payload
    )

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

    incidents = correlator.correlate(
        signals
    )

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

    evidence_engine = EvidenceEngine()

    return evidence_engine.build_packet(
        incident=incident,
        signals=incident_signals,
        observations=incident_observations,
    )


def test_diagnosis_returns_all_catalog_hypotheses():
    packet = _get_evidence_packet()

    engine = DiagnosisEngine()

    hypotheses = engine.diagnose(packet)

    assert len(hypotheses) == 12

    keys = {
        hypothesis.hypothesis
        for hypothesis in hypotheses
    }

    assert "technical_availability" in keys
    assert "crawl_indexation" in keys
    assert "ctr_snippet_regression" in keys
    assert "demand_seasonality" in keys


def test_diagnosis_keeps_cause_unestablished():
    packet = _get_evidence_packet()

    engine = DiagnosisEngine()

    hypotheses = engine.diagnose(packet)

    for hypothesis in hypotheses:
        assert hypothesis.unknowns
        assert hypothesis.confidence_components.authority == 0.0
        assert hypothesis.confidence_components.coverage == 0.0
        assert hypothesis.confidence_components.agreement == 0.0
        assert hypothesis.confidence_components.recency == 0.0


def test_diagnosis_contains_next_checks():
    packet = _get_evidence_packet()

    engine = DiagnosisEngine()

    hypotheses = engine.diagnose(packet)

    technical = next(
        hypothesis
        for hypothesis in hypotheses
        if hypothesis.hypothesis
        == "technical_availability"
    )

    assert technical.next_check
    assert (
        "uptime"
        in technical.next_check[0].lower()
    )