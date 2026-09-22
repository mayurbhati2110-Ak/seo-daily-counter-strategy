from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """
    Common contract for all external data connectors.

    Provider-specific logic belongs in concrete connector
    implementations, not in this base class.
    """

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Return the current health/status of the connector."""
        raise NotImplementedError

    @abstractmethod
    def fetch(
        self,
        date_range: tuple[str, str],
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch raw provider data for the requested date range.

        The raw provider response should be preserved before
        normalization.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw_payload: dict[str, Any]) -> list[Any]:
        """Convert provider-specific data into canonical observations."""
        raise NotImplementedError

    @abstractmethod
    def freshness(self) -> dict[str, Any]:
        """Return freshness information for the connector's data."""
        raise NotImplementedError

    @abstractmethod
    def provenance(self) -> dict[str, Any]:
        """Return source and retrieval provenance information."""
        raise NotImplementedError