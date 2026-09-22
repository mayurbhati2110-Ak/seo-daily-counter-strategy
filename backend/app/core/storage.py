from collections import defaultdict
from typing import Iterable

from app.models.observation import Observation


class ObservationStore:
    """
    In-memory observation store for the MVP.

    The interface is intentionally small so a PostgreSQL-backed
    implementation can replace it later without changing the
    rest of the pipeline.
    """

    def __init__(self) -> None:
        self._observations: dict[str, Observation] = {}

    def save(self, observation: Observation) -> Observation:
        """Save or replace an observation by its stable ID."""
        self._observations[observation.observation_id] = observation
        return observation

    def save_many(
        self,
        observations: Iterable[Observation],
    ) -> int:
        """Save multiple observations and return the number stored."""
        count = 0

        for observation in observations:
            self.save(observation)
            count += 1

        return count

    def get(self, observation_id: str) -> Observation | None:
        """Return an observation by ID."""
        return self._observations.get(observation_id)

    def list_by_site(self, site_id: str) -> list[Observation]:
        """Return all observations belonging to a site."""
        return [
            observation
            for observation in self._observations.values()
            if observation.site_id == site_id
        ]

    def list_by_metric(
        self,
        site_id: str,
        metric: str,
    ) -> list[Observation]:
        """Return observations for a site and metric."""
        return [
            observation
            for observation in self._observations.values()
            if observation.site_id == site_id
            and observation.metric == metric
        ]

    def count(self) -> int:
        """Return the total number of stored observations."""
        return len(self._observations)

    def clear(self) -> None:
        """Clear the store. Primarily useful for tests."""
        self._observations.clear()