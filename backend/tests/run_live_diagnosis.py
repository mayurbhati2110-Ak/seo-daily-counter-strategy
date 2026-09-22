from pathlib import Path

from app.connectors.gsc import GSCMockConnector
from app.diagnosis.evidence import EvidenceEngine
from app.diagnosis.llm_client import DiagnosisLLMClient
from app.pipeline.correlator import IncidentCorrelator
from app.pipeline.detector import SearchPerformanceDetector
from app.pipeline.normalizer import ObservationNormalizer


FIXTURES_DIR = (
    Path(__file__).resolve().parents[1]
    / "tests"
    / "fixtures"
)

# Correct fixture location from backend/
GSC_FIXTURES = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def main():
    connector = GSCMockConnector(GSC_FIXTURES)
    normalizer = ObservationNormalizer()

    raw = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw)

    baseline = [
        item
        for item in observations
        if item.observed_at.strftime("%Y-%m-%d")
        == "2026-09-18"
    ]

    current = [
        item
        for item in observations
        if item.observed_at.strftime("%Y-%m-%d")
        == "2026-09-20"
    ]

    detector = SearchPerformanceDetector()

    signals = detector.detect(
        baseline,
        current,
    )

    correlator = IncidentCorrelator()

    incidents = correlator.correlate(signals)

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

    packet = evidence_engine.build_packet(
        incident=incident,
        signals=incident_signals,
        observations=incident_observations,
    )

    client = DiagnosisLLMClient()

    print("========================================")
    print("LIVE SEO DIAGNOSIS")
    print("========================================")
    print(f"Base URL : {client.base_url}")
    print(f"Model    : {client.model}")
    print(f"Incident : {packet.incident_id}")
    print(f"Target   : {packet.target}")
    print(
        f"Evidence : {len(packet.evidence_items)}"
    )
    print()

    result = client.diagnose(packet)

    print("LLM DIAGNOSIS")
    print("----------------------------------------")
    print(
        "Likely hypotheses:",
        result.likely_hypotheses,
    )
    print()
    print(
        "Evidence for:",
        result.evidence_for,
    )
    print()
    print(
        "Evidence against:",
        result.evidence_against,
    )
    print()
    print(
        "Unknowns:",
        result.unknowns,
    )
    print()
    print(
        "Next checks:",
        result.next_check,
    )
    print()
    print(
        "Cause established:",
        result.cause_established,
    )
    print("========================================")


if __name__ == "__main__":
    main()