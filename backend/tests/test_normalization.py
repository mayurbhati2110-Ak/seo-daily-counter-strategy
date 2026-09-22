from pathlib import Path

from app.connectors.gsc import GSCMockConnector
from app.models.observation import DataStatus, SourceTier
from app.pipeline.normalizer import ObservationNormalizer


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def test_gsc_normalization():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw_payload)

    assert len(observations) == 24

    first = observations[0]

    assert first.site_id == "spearmint"
    assert first.source == "gsc"
    assert first.source_tier == SourceTier.T1
    assert first.status == DataStatus.VALID
    assert first.url.startswith("https://spearmint.online/")
    assert first.query is not None
    assert first.country == "IND"
    assert first.device in {"DESKTOP", "MOBILE"}
    assert first.provenance["source"] == "gsc"
    assert first.provenance["source_tier"] == "T1"


def test_gsc_normalization_contains_expected_metrics():
    connector = GSCMockConnector(FIXTURES_DIR)
    normalizer = ObservationNormalizer()

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = normalizer.normalize(raw_payload)

    metrics = {observation.metric for observation in observations}

    assert metrics == {
        "clicks",
        "impressions",
        "ctr",
        "position",
    }