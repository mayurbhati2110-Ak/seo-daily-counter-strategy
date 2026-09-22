from app.diagnosis.catalog import HypothesisCatalog


def test_hypothesis_catalog_contains_required_families():
    catalog = HypothesisCatalog()

    expected = {
        "technical_availability",
        "crawl_indexation",
        "deployment_content_regression",
        "serp_intent_feature",
        "competitor_improvement",
        "ctr_snippet_regression",
        "cannibalization",
        "internal_linking_authority",
        "backlink_loss",
        "demand_seasonality",
        "core_web_vitals",
        "measurement_freshness",
    }

    assert set(catalog.keys()) == expected


def test_hypothesis_catalog_returns_definition():
    catalog = HypothesisCatalog()

    definition = catalog.get(
        "ctr_snippet_regression"
    )

    assert definition is not None
    assert definition.key == "ctr_snippet_regression"
    assert definition.name == "CTR/snippet regression"


def test_hypothesis_catalog_rejects_unknown_family():
    catalog = HypothesisCatalog()

    assert catalog.get("made_up_cause") is None
    assert catalog.contains("made_up_cause") is False