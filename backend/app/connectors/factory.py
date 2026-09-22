from pathlib import Path

from app.connectors.base import BaseConnector
from app.connectors.gsc import GSCMockConnector
from app.connectors.gsc_real import GSCRealConnector


def create_gsc_connector(
    mode: str,
    *,
    fixtures_dir: str | Path,
    site_url: str = "",
    credentials_path: str | Path | None = None,
) -> BaseConnector:
    """
    Create the requested GSC connector.

    Supported modes:
        - mock: deterministic fixture connector
        - real: Google Search Console connector

    The mock connector remains the safe default path for
    development and fixture replay.
    """

    normalized_mode = mode.strip().lower()

    if normalized_mode == "mock":
        return GSCMockConnector(
            fixtures_dir=fixtures_dir,
        )

    if normalized_mode == "real":
        return GSCRealConnector(
            site_url=site_url,
            credentials_path=credentials_path,
        )

    raise ValueError(
        f"Unsupported GSC connector mode: {mode!r}. "
        "Expected 'mock' or 'real'."
    )