from pathlib import Path
from typing import Any
import json

from app.connectors.base import BaseConnector


class GSCMockConnector(BaseConnector):
    """
    Mock Google Search Console connector.

    Reads deterministic fixture data from the project fixtures directory.
    This is used during development before the real GSC integration exists.
    """

    def __init__(self, fixtures_dir: str | Path):
        self.fixtures_dir = Path(fixtures_dir)

    def health(self) -> dict[str, Any]:
        baseline = self.fixtures_dir / "search_performance_baseline.json"
        current = self.fixtures_dir / "search_performance_current.json"

        return {
            "connector": "gsc",
            "mode": "mock",
            "healthy": baseline.exists() and current.exists(),
        }

    def fetch(
        self,
        date_range: tuple[str, str],
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Return fixture data matching the requested period.

        For the MVP mock connector, the available fixture snapshots
        are returned rather than making an external API request.
        """

        start_date, end_date = date_range

        baseline = self._load_fixture("search_performance_baseline.json")
        current = self._load_fixture("search_performance_current.json")

        return {
            "source": "gsc",
            "mode": "mock",
            "date_range": {
                "start": start_date,
                "end": end_date,
            },
            "cursor": cursor,
            "snapshots": [
                baseline,
                current,
            ],
        }

    def normalize(self, raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Convert GSC fixture rows into canonical observation-shaped data.

        Full Observation model construction will be added when the
        normalization pipeline is implemented.
        """

        observations: list[dict[str, Any]] = []

        for snapshot in raw_payload.get("snapshots", []):
            for row in snapshot.get("rows", []):
                observations.append(
                    {
                        "site_id": snapshot["site_id"],
                        "source": snapshot["source"],
                        "source_tier": snapshot["source_tier"],
                        "observed_at": row["date"],
                        "url": row["url"],
                        "query": row["query"],
                        "country": row["country"],
                        "device": row["device"],
                        "clicks": row["clicks"],
                        "impressions": row["impressions"],
                        "ctr": row["ctr"],
                        "position": row["position"],
                    }
                )

        return observations

    def freshness(self) -> dict[str, Any]:
        baseline = self._load_fixture("search_performance_baseline.json")
        current = self._load_fixture("search_performance_current.json")

        return {
            "source": "gsc",
            "baseline_retrieved_at": baseline.get("retrieved_at"),
            "current_retrieved_at": current.get("retrieved_at"),
            "status": baseline.get("status", "unknown"),
        }

    def provenance(self) -> dict[str, Any]:
        return {
            "source": "gsc",
            "source_tier": "T1",
            "connector": "GSCMockConnector",
            "mode": "mock",
            "fixtures": [
                "search_performance_baseline.json",
                "search_performance_current.json",
            ],
        }

    def _load_fixture(self, filename: str) -> dict[str, Any]:
        path = self.fixtures_dir / filename

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)