from pydantic import BaseModel, Field


class SiteConfig(BaseModel):
    """
    Configuration boundary for one monitored website.

    Unknown site information must be supplied by configuration;
    the system must not invent it.
    """

    site_id: str = Field(..., min_length=1)
    canonical_domain: str = Field(..., min_length=1)

    markets: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)

    device_focus: list[str] = Field(
        default_factory=lambda: ["desktop", "mobile"]
    )

    money_pages: list[str] = Field(default_factory=list)
    important_page_groups: list[str] = Field(default_factory=list)

    competitors: list[str] = Field(default_factory=list)

    business_kpis: list[str] = Field(default_factory=list)
    conversion_definitions: list[str] = Field(default_factory=list)

    owners: list[str] = Field(default_factory=list)

    detector_thresholds: dict[str, float] = Field(default_factory=dict)
    priority_weights: dict[str, float] = Field(default_factory=dict)

    collection_cadence: str = "daily"
    freshness_expectations: dict[str, str] = Field(default_factory=dict)