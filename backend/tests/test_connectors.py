from pathlib import Path

from app.connectors.gsc import GSCMockConnector


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gsc"
)


def test_gsc_mock_connector_health():
    connector = GSCMockConnector(FIXTURES_DIR)

    result = connector.health()

    assert result["connector"] == "gsc"
    assert result["mode"] == "mock"
    assert result["healthy"] is True


def test_gsc_mock_connector_fetch():
    connector = GSCMockConnector(FIXTURES_DIR)

    result = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    assert result["source"] == "gsc"
    assert result["mode"] == "mock"
    assert len(result["snapshots"]) == 2


def test_gsc_mock_connector_normalize():
    connector = GSCMockConnector(FIXTURES_DIR)

    raw_payload = connector.fetch(
        ("2026-09-18", "2026-09-20")
    )

    observations = connector.normalize(raw_payload)

    assert len(observations) == 6
    assert observations[0]["site_id"] == "spearmint"
    assert observations[0]["source"] == "gsc"
    assert observations[0]["source_tier"] == "T1"


def test_gsc_mock_connector_provenance():
    connector = GSCMockConnector(FIXTURES_DIR)

    provenance = connector.provenance()

    assert provenance["source"] == "gsc"
    assert provenance["source_tier"] == "T1"
    assert provenance["mode"] == "mock"