from datetime import datetime, timezone
from typing import Iterable

from app.models.evidence import (
    EvidenceItem,
    EvidencePacket,
    EvidenceRole,
)
from app.models.incident import Incident
from app.models.observation import Observation
from app.models.signal import Signal


class EvidenceEngine:
    """
    Builds a traceable evidence packet for an incident.

    The engine is deterministic and does not infer a cause.
    """

    VERSION = "evidence-engine-v1"

    def build_packet(
        self,
        incident: Incident,
        signals: Iterable[Signal],
        observations: Iterable[Observation],
    ) -> EvidencePacket:
        signals = list(signals)
        observations = list(observations)

        evidence_items: list[EvidenceItem] = []

        for signal in signals:
            evidence_items.append(
                self._signal_evidence(signal)
            )

        for observation in observations:
            if not self._belongs_to_incident(
                observation,
                incident,
            ):
                continue

            evidence_items.append(
                self._observation_evidence(observation)
            )

        detector_versions = sorted(
            {
                signal.detector_version
                for signal in signals
            }
        )

        timestamps = [
            observation.observed_at
            for observation in observations
            if self._belongs_to_incident(
                observation,
                incident,
            )
        ]

        if timestamps:
            window_start = min(timestamps)
            window_end = max(timestamps)
        else:
            window_start = incident.started_at
            window_end = incident.detected_at

        return EvidencePacket(
            incident_id=incident.incident_id,
            status=incident.status.value,
            target=incident.target,
            window_start=window_start,
            window_end=window_end,
            signal_ids=[
                signal.signal_id
                for signal in signals
            ],
            evidence_items=evidence_items,
            contradictions=[],
            missing_checks=[],
            recent_changes=[],
            constraints=[],
            detector_versions=detector_versions,
            metadata={
                "engine_version": self.VERSION,
                "cause_established": incident.cause_established,
                "evidence_count": len(evidence_items),
            },
        )

    def _signal_evidence(
        self,
        signal: Signal,
    ) -> EvidenceItem:
        observed_at = signal.detected_at
        retrieved_at = signal.detected_at

        return EvidenceItem(
            evidence_id=f"signal:{signal.signal_id}",
            source="deterministic_detector",
            source_tier="T1",
            fact=(
                f"{signal.metric} changed from "
                f"{signal.baseline_value} to "
                f"{signal.current_value}"
            ),
            metric=signal.metric,
            value=signal.current_value,
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            freshness_status="valid",
            role=EvidenceRole.SUPPORTING,
            provenance={
                "signal_id": signal.signal_id,
                "detector_version": signal.detector_version,
                "url": signal.url,
                "query": signal.query,
            },
        )

    def _observation_evidence(
        self,
        observation: Observation,
    ) -> EvidenceItem:
        evidence_id = (
            f"observation:{observation.observation_id}"
        )

        return EvidenceItem(
            evidence_id=evidence_id,
            source=observation.source,
            source_tier=observation.source_tier.value,
            fact=(
                f"{observation.metric} = "
                f"{observation.value}"
            ),
            metric=observation.metric,
            value=observation.value,
            observed_at=observation.observed_at,
            retrieved_at=observation.retrieved_at,
            freshness_status=observation.status.value,
            role=EvidenceRole.CONTEXT,
            provenance=observation.provenance,
        )

    @staticmethod
    def _belongs_to_incident(
        observation: Observation,
        incident: Incident,
    ) -> bool:
        if observation.site_id != incident.site_id:
            return False

        if incident.page and observation.url != incident.page:
            return False

        if incident.query and observation.query != incident.query:
            return False

        return True