from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.connectors.base import BaseConnector


class GSCRealConnector(BaseConnector):
    """
    Real Google Search Console connector.

    Uses a Google service-account credential to query the
    Search Analytics API.

    The connector only fetches and normalizes data.
    It does not modify anything in Google Search Console.
    """

    SOURCE = "gsc"
    SOURCE_TIER = "T1"

    SCOPES = [
        "https://www.googleapis.com/auth/webmasters.readonly"
    ]

    ROW_LIMIT = 25_000

    def __init__(
        self,
        site_url: str,
        credentials_path: str | Path | None = None,
    ) -> None:
        self.site_url = site_url
        self.credentials_path = (
            Path(credentials_path)
            if credentials_path
            else None
        )

        self._service = None
        self._last_retrieved_at: str | None = None
        self._last_date_range: tuple[str, str] | None = None

    def _get_service(self):
        """
        Lazily create the Google Search Console API client.

        Credentials are not loaded until the real connector is
        actually used.
        """

        if self._service is None:
            if self.credentials_path is None:
                raise RuntimeError(
                    "GSC credentials path is not configured."
                )

            if not self.credentials_path.exists():
                raise FileNotFoundError(
                    f"GSC credentials file not found: "
                    f"{self.credentials_path}"
                )

            credentials = (
                service_account.Credentials
                .from_service_account_file(
                    str(self.credentials_path),
                    scopes=self.SCOPES,
                )
            )

            self._service = build(
                "searchconsole",
                "v1",
                credentials=credentials,
                cache_discovery=False,
            )

        return self._service

    def health(self) -> dict[str, Any]:
        """
        Check whether the connector is configured.

        This performs a lightweight credential/client check,
        but does not execute a Search Analytics query.
        """

        if not self.site_url:
            return {
                "connector": self.SOURCE,
                "mode": "real",
                "healthy": False,
                "reason": "site_url_not_configured",
            }

        if self.credentials_path is None:
            return {
                "connector": self.SOURCE,
                "mode": "real",
                "healthy": False,
                "reason": "credentials_path_not_configured",
            }

        if not self.credentials_path.exists():
            return {
                "connector": self.SOURCE,
                "mode": "real",
                "healthy": False,
                "reason": "credentials_file_not_found",
            }

        try:
            self._get_service()

            return {
                "connector": self.SOURCE,
                "mode": "real",
                "healthy": True,
                "site_url": self.site_url,
            }

        except Exception as exc:
            return {
                "connector": self.SOURCE,
                "mode": "real",
                "healthy": False,
                "reason": "client_initialization_failed",
                "error": str(exc),
            }

    def fetch(
        self,
        date_range: tuple[str, str],
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch Search Analytics data for the requested date range.

        The raw Google response is preserved inside the returned
        payload so provenance and evidence can be retained.
        """

        start_date, end_date = date_range

        request_body: dict[str, Any] = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": [
                "date",
                "page",
                "query",
                "country",
                "device",
            ],
            "rowLimit": self.ROW_LIMIT,
        }

        if cursor is not None:
            request_body["startRow"] = int(cursor)

        service = self._get_service()

        response = (
            service
            .searchanalytics()
            .query(
                siteUrl=self.site_url,
                body=request_body,
            )
            .execute()
        )

        retrieved_at = datetime.now(
            timezone.utc
        ).isoformat()

        self._last_retrieved_at = retrieved_at
        self._last_date_range = date_range

        rows = []

        for row in response.get("rows", []):
            keys = row.get("keys", [])

            rows.append(
                {
                    "date": (
                        keys[0]
                        if len(keys) > 0
                        else None
                    ),
                    "url": (
                        keys[1]
                        if len(keys) > 1
                        else None
                    ),
                    "query": (
                        keys[2]
                        if len(keys) > 2
                        else None
                    ),
                    "country": (
                        keys[3]
                        if len(keys) > 3
                        else None
                    ),
                    "device": (
                        keys[4]
                        if len(keys) > 4
                        else None
                    ),
                    "clicks": row.get("clicks"),
                    "impressions": row.get("impressions"),
                    "ctr": row.get("ctr"),
                    "position": row.get("position"),
                }
            )

        next_cursor = None

        if len(rows) == self.ROW_LIMIT:
            current_start = (
                int(cursor)
                if cursor is not None
                else 0
            )

            next_cursor = str(
                current_start + len(rows)
            )

        return {
            "source": self.SOURCE,
            "mode": "real",
            "site_id": self.site_url,
            "source_tier": self.SOURCE_TIER,
            "date_range": {
                "start": start_date,
                "end": end_date,
            },
            "retrieved_at": retrieved_at,
            "status": "valid",
            "cursor": cursor,
            "next_cursor": next_cursor,
            "rows": rows,

            # Preserve original provider response.
            "raw_response": response,
        }

    def normalize(
        self,
        raw_payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Convert the real GSC response into the canonical
        observation shape used by the existing pipeline.
        """

        observations: list[dict[str, Any]] = []

        for row in raw_payload.get("rows", []):
            observations.append(
                {
                    "site_id": raw_payload.get(
                        "site_id",
                        self.site_url,
                    ),
                    "source": self.SOURCE,
                    "source_tier": self.SOURCE_TIER,
                    "observed_at": row.get("date"),
                    "url": row.get("url"),
                    "query": row.get("query"),
                    "country": row.get("country"),
                    "device": row.get("device"),
                    "clicks": row.get("clicks"),
                    "impressions": row.get("impressions"),
                    "ctr": row.get("ctr"),
                    "position": row.get("position"),
                }
            )

        return observations

    def freshness(self) -> dict[str, Any]:
        return {
            "source": self.SOURCE,
            "mode": "real",
            "retrieved_at": self._last_retrieved_at,
            "date_range": (
                {
                    "start": self._last_date_range[0],
                    "end": self._last_date_range[1],
                }
                if self._last_date_range
                else None
            ),
        }

    def provenance(self) -> dict[str, Any]:
        return {
            "source": self.SOURCE,
            "source_tier": self.SOURCE_TIER,
            "connector": self.__class__.__name__,
            "mode": "real",
            "site_url": self.site_url,
        }