from datetime import datetime, timezone
from typing import Any

from app.models.observation import (
    DataStatus,
    Observation,
    SourceTier,
)


class ObservationNormalizer:
    """
    Converts connector output into canonical Observation objects.

    Provider-specific payload shapes should not leak into the
    rest of the pipeline.
    """

    def normalize(
        self,
        raw_payload: dict[str, Any],
    ) -> list[Observation]:
        observations: list[Observation] = []

        for snapshot in raw_payload.get("snapshots", []):
            site_id = snapshot["site_id"]
            source = snapshot["source"]
            source_tier = SourceTier(snapshot["source_tier"])
            retrieved_at = datetime.fromisoformat(
                snapshot["retrieved_at"].replace("Z", "+00:00")
            )

            status = DataStatus(snapshot.get("status", "valid"))

            for row in snapshot.get("rows", []):
                observed_at = datetime.fromisoformat(
                    row["date"]
                ).replace(tzinfo=timezone.utc)

                dimensions = {
                    "url": row.get("url"),
                    "query": row.get("query"),
                    "country": row.get("country"),
                    "device": row.get("device"),
                }

                metric_values = {
                    "clicks": row.get("clicks"),
                    "impressions": row.get("impressions"),
                    "ctr": row.get("ctr"),
                    "position": row.get("position"),
                }

                for metric, value in metric_values.items():
                    observations.append(
                        Observation(
                            observation_id=(
                                f"{site_id}:"
                                f"{source}:"
                                f"{row['date']}:"
                                f"{row.get('url', '')}:"
                                f"{row.get('query', '')}:"
                                f"{metric}"
                            ),
                            site_id=site_id,
                            source=source,
                            source_tier=source_tier,
                            metric=metric,
                            value=value,
                            observed_at=observed_at,
                            retrieved_at=retrieved_at,
                            status=status,
                            **dimensions,
                            provenance={
                                "source": source,
                                "source_tier": source_tier.value,
                                "retrieved_at": snapshot["retrieved_at"],
                                "connector_mode": raw_payload.get(
                                    "mode",
                                    "unknown",
                                ),
                            },
                            metadata={
                                "date_range": raw_payload.get(
                                    "date_range"
                                ),
                            },
                        )
                    )

        return observations