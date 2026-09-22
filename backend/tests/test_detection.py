from pathlib import Path

from app.connectors.gsc import GSCMockConnector
from app.pipeline.detector import SearchPerformanceDetector
from app.pipeline.normalizer import ObservationNormalizer
from app.models.signal import SignalDirection, SignalType


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def test_search_performance_detector():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw_payload)

    baseline = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d") == "2026-09-18"
    ]

    current = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d") == "2026-09-20"
    ]

    detector = SearchPerformanceDetector()

    signals = detector.detect(
        baseline=baseline,
        current=current,
    )

    assert len(signals) == 3

    metrics = {signal.metric for signal in signals}

    assert metrics == {
        "clicks",
        "ctr",
        "position",
    }

    for signal in signals:
        assert signal.site_id == "spearmint"
        assert signal.signal_type == SignalType.SEARCH_PERFORMANCE
        assert signal.direction in {
            SignalDirection.DOWN,
            SignalDirection.UP,
        }
        assert signal.detector_version == "search-performance-v1"
        assert signal.url == "https://spearmint.online/pricing"
        assert signal.query == "seo software pricing"


def test_search_performance_detector_ignores_stable_pages():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw_payload)

    baseline = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d") == "2026-09-18"
    ]

    current = [
        observation
        for observation in observations
        if observation.observed_at.strftime("%Y-%m-%d") == "2026-09-20"
    ]

    detector = SearchPerformanceDetector()

    signals = detector.detect(
        baseline=baseline,
        current=current,
    )

    signal_urls = {signal.url for signal in signals}

    assert "https://spearmint.online/products" not in signal_urls
    assert "https://spearmint.online/blog/seo-guide" not in signal_urls