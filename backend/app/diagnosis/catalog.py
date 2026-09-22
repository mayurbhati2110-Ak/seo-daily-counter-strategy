from dataclasses import dataclass


@dataclass(frozen=True)
class HypothesisDefinition:
    """
    A controlled diagnosis hypothesis family.

    The catalog defines what the diagnosis engine is allowed
    to consider. It does not establish which hypothesis is true.
    """

    key: str
    name: str
    description: str


class HypothesisCatalog:
    """
    Registry of allowed SEO diagnosis hypothesis families.
    """

    VERSION = "hypothesis-catalog-v1"

    def __init__(self) -> None:
        self._definitions = {
            "technical_availability": HypothesisDefinition(
                key="technical_availability",
                name="Technical availability",
                description=(
                    "The target may be affected by availability, "
                    "server, or accessibility problems."
                ),
            ),
            "crawl_indexation": HypothesisDefinition(
                key="crawl_indexation",
                name="Crawl/indexation",
                description=(
                    "The target may have changed in crawlability "
                    "or search indexation."
                ),
            ),
            "deployment_content_regression": HypothesisDefinition(
                key="deployment_content_regression",
                name="Deployment/content regression",
                description=(
                    "A recent deployment or content change may "
                    "have affected search performance."
                ),
            ),
            "serp_intent_feature": HypothesisDefinition(
                key="serp_intent_feature",
                name="SERP intent/feature",
                description=(
                    "Changes in search intent or SERP features may "
                    "have affected the target."
                ),
            ),
            "competitor_improvement": HypothesisDefinition(
                key="competitor_improvement",
                name="Competitor improvement",
                description=(
                    "A competitor may have improved its search "
                    "visibility or relevance."
                ),
            ),
            "ctr_snippet_regression": HypothesisDefinition(
                key="ctr_snippet_regression",
                name="CTR/snippet regression",
                description=(
                    "A change in search-result presentation or "
                    "snippet attractiveness may have reduced CTR."
                ),
            ),
            "cannibalization": HypothesisDefinition(
                key="cannibalization",
                name="Cannibalization",
                description=(
                    "Multiple pages may be competing for the same "
                    "query or search intent."
                ),
            ),
            "internal_linking_authority": HypothesisDefinition(
                key="internal_linking_authority",
                name="Internal linking/authority",
                description=(
                    "Changes in internal linking or page authority "
                    "may have affected visibility."
                ),
            ),
            "backlink_loss": HypothesisDefinition(
                key="backlink_loss",
                name="Backlink loss",
                description=(
                    "Loss or weakening of external links may have "
                    "affected search visibility."
                ),
            ),
            "demand_seasonality": HypothesisDefinition(
                key="demand_seasonality",
                name="Demand/seasonality",
                description=(
                    "Changes in search demand or seasonal behavior "
                    "may explain the observed movement."
                ),
            ),
            "core_web_vitals": HypothesisDefinition(
                key="core_web_vitals",
                name="Core Web Vitals",
                description=(
                    "Page experience or Core Web Vitals changes may "
                    "have contributed to the observed movement."
                ),
            ),
            "measurement_freshness": HypothesisDefinition(
                key="measurement_freshness",
                name="Measurement freshness",
                description=(
                    "Stale, delayed, partial, or otherwise limited "
                    "measurement data may explain the observation."
                ),
            ),
        }

    def get(self, key: str) -> HypothesisDefinition | None:
        return self._definitions.get(key)

    def list_all(self) -> list[HypothesisDefinition]:
        return list(self._definitions.values())

    def keys(self) -> list[str]:
        return list(self._definitions.keys())

    def contains(self, key: str) -> bool:
        return key in self._definitions