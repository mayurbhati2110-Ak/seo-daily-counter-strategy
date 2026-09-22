from typing import Iterable

from app.models.observation import Observation
from app.models.signal import (
    Signal,
    SignalDirection,
    SignalType,
)


class SearchPerformanceDetector:
    """
    Deterministic detector for GSC search-performance regressions.

    The detector compares two observation periods for the same
    page/query/device/country combination.
    """

    VERSION = "search-performance-v1"

    def __init__(
        self,
        clicks_drop_threshold: float = 0.20,
        ctr_drop_threshold: float = 0.20,
        position_increase_threshold: float = 0.20,
        minimum_clicks: int = 50,
    ) -> None:
        self.clicks_drop_threshold = clicks_drop_threshold
        self.ctr_drop_threshold = ctr_drop_threshold
        self.position_increase_threshold = position_increase_threshold
        self.minimum_clicks = minimum_clicks

    def detect(
        self,
        baseline: Iterable[Observation],
        current: Iterable[Observation],
    ) -> list[Signal]:
        baseline_map = self._index(baseline)
        current_map = self._index(current)

        signals: list[Signal] = []

        for key, current_metrics in current_map.items():
            baseline_metrics = baseline_map.get(key)

            if baseline_metrics is None:
                continue

            baseline_clicks = baseline_metrics.get("clicks")
            current_clicks = current_metrics.get("clicks")

            if (
                baseline_clicks is None
                or current_clicks is None
                or baseline_clicks < self.minimum_clicks
            ):
                continue

            target = key[0]
            query = key[1]

            signals.extend(
                self._detect_clicks(
                    key,
                    baseline_clicks,
                    current_clicks,
                    target,
                    query,
                )
            )

            signals.extend(
                self._detect_ctr(
                    key,
                    baseline_metrics.get("ctr"),
                    current_metrics.get("ctr"),
                    target,
                    query,
                )
            )

            signals.extend(
                self._detect_position(
                    key,
                    baseline_metrics.get("position"),
                    current_metrics.get("position"),
                    target,
                    query,
                )
            )

        return signals

    def _detect_clicks(
        self,
        key: tuple,
        baseline: float,
        current: float,
        target: str,
        query: str,
    ) -> list[Signal]:
        change_percent = self._percent_change(
            baseline,
            current,
        )

        if change_percent <= -self.clicks_drop_threshold * 100:
            return [
                self._build_signal(
                    key=key,
                    metric="clicks",
                    direction=SignalDirection.DOWN,
                    current=current,
                    baseline=baseline,
                    change_percent=change_percent,
                    target=target,
                    query=query,
                )
            ]

        return []

    def _detect_ctr(
        self,
        key: tuple,
        baseline: float | None,
        current: float | None,
        target: str,
        query: str,
    ) -> list[Signal]:
        if baseline is None or current is None or baseline == 0:
            return []

        change_percent = self._percent_change(
            baseline,
            current,
        )

        if change_percent <= -self.ctr_drop_threshold * 100:
            return [
                self._build_signal(
                    key=key,
                    metric="ctr",
                    direction=SignalDirection.DOWN,
                    current=current,
                    baseline=baseline,
                    change_percent=change_percent,
                    target=target,
                    query=query,
                )
            ]

        return []

    def _detect_position(
        self,
        key: tuple,
        baseline: float | None,
        current: float | None,
        target: str,
        query: str,
    ) -> list[Signal]:
        if baseline is None or current is None or baseline == 0:
            return []

        change_percent = self._percent_change(
            baseline,
            current,
        )

        if change_percent >= self.position_increase_threshold * 100:
            return [
                self._build_signal(
                    key=key,
                    metric="position",
                    direction=SignalDirection.UP,
                    current=current,
                    baseline=baseline,
                    change_percent=change_percent,
                    target=target,
                    query=query,
                )
            ]

        return []

    def _index(
        self,
        observations: Iterable[Observation],
    ) -> dict[tuple, dict[str, float]]:
        indexed: dict[tuple, dict[str, float]] = {}

        for observation in observations:
            if observation.metric not in {
                "clicks",
                "impressions",
                "ctr",
                "position",
            }:
                continue

            key = (
                observation.url,
                observation.query,
                observation.country,
                observation.device,
            )

            indexed.setdefault(key, {})
            indexed[key][observation.metric] = observation.value

        return indexed

    @staticmethod
    def _percent_change(
        baseline: float,
        current: float,
    ) -> float:
        if baseline == 0:
            return 0.0

        return ((current - baseline) / baseline) * 100

    def _build_signal(
        self,
        key: tuple,
        metric: str,
        direction: SignalDirection,
        current: float,
        baseline: float,
        change_percent: float,
        target: str,
        query: str,
    ) -> Signal:
        url, _, country, device = key

        return Signal(
            signal_id=(
                f"{self.VERSION}:"
                f"{url}:"
                f"{query}:"
                f"{metric}"
            ),
            site_id="spearmint",
            signal_type=SignalType.SEARCH_PERFORMANCE,
            direction=direction,
            metric=metric,
            current_value=current,
            baseline_value=baseline,
            change_percent=change_percent,
            target=target,
            url=url,
            query=query,
            detected_at=current_observed_at(),
            observation_ids=[],
            detector_version=self.VERSION,
            metadata={
                "country": country,
                "device": device,
                "thresholds": {
                    "clicks_drop": self.clicks_drop_threshold,
                    "ctr_drop": self.ctr_drop_threshold,
                    "position_increase": self.position_increase_threshold,
                    "minimum_clicks": self.minimum_clicks,
                },
            },
        )


def current_observed_at():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc)