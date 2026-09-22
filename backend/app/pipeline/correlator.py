from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterable

from app.models.incident import Incident, IncidentStatus
from app.models.signal import Signal


class IncidentCorrelator:
    """
    Groups related signals into incidents.

    V1 correlation is deterministic:
    - same site
    - same URL
    - overlapping target/query context
    - same general detection period

    Correlation does not establish causation.
    """

    VERSION = "incident-correlation-v1"

    def correlate(
        self,
        signals: Iterable[Signal],
    ) -> list[Incident]:
        grouped: dict[tuple, list[Signal]] = defaultdict(list)

        for signal in signals:
            key = (
                signal.site_id,
                signal.url,
                signal.query,
            )
            grouped[key].append(signal)

        incidents: list[Incident] = []

        for index, ((site_id, url, query), group) in enumerate(
            grouped.items(),
            start=1,
        ):
            if not group:
                continue

            detected_times = [
                signal.detected_at
                for signal in group
            ]

            started_at = min(detected_times)
            detected_at = max(detected_times)

            incidents.append(
                Incident(
                    incident_id=(
                        f"{self.VERSION}:"
                        f"{site_id}:"
                        f"{url}:"
                        f"{query}:"
                        f"{index}"
                    ),
                    site_id=site_id,
                    status=IncidentStatus.NEW,
                    target=url,
                    page=url,
                    query=query,
                    started_at=started_at,
                    detected_at=detected_at,
                    signal_ids=[
                        signal.signal_id
                        for signal in group
                    ],
                    evidence_ids=[],
                    cause_established=False,
                    metadata={
                        "correlation_version": self.VERSION,
                        "signal_count": len(group),
                        "metrics": [
                            signal.metric
                            for signal in group
                        ],
                    },
                )
            )

        return incidents