from app.models.site import SiteConfig


def test_site_config():
    site = SiteConfig(
        site_id="demo-site",
        canonical_domain="https://example.com",
        markets=["IN"],
        languages=["en"],
        money_pages=["/pricing", "/products"],
        competitors=["competitor-a.com"],
        business_kpis=["organic_clicks", "conversions"],
    )

    assert site.site_id == "demo-site"
    assert site.canonical_domain == "https://example.com"
    assert "/pricing" in site.money_pages