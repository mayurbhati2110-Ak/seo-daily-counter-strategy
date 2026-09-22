from app.diagnosis.catalog import HypothesisCatalog
from app.models.evidence import EvidencePacket, EvidenceRole
from app.models.hypothesis import (
    ConfidenceComponents,
    Hypothesis,
)


class DiagnosisEngine:
    """
    Deterministic diagnosis engine.

    This layer does not invent causes. It evaluates the available
    evidence against controlled hypothesis families and explicitly
    records unknowns when evidence is insufficient.
    """

    VERSION = "diagnosis-engine-v1"

    def __init__(
        self,
        catalog: HypothesisCatalog | None = None,
    ) -> None:
        self.catalog = catalog or HypothesisCatalog()

    def diagnose(
        self,
        packet: EvidencePacket,
    ) -> list[Hypothesis]:
        hypotheses: list[Hypothesis] = []

        for definition in self.catalog.list_all():
            hypothesis = self._evaluate_hypothesis(
                definition.key,
                packet,
            )

            hypotheses.append(hypothesis)

        return hypotheses

    def _evaluate_hypothesis(
        self,
        key: str,
        packet: EvidencePacket,
    ) -> Hypothesis:
        supporting = [
            item.evidence_id
            for item in packet.evidence_items
            if item.role == EvidenceRole.SUPPORTING
        ]

        contradicting = [
            item.evidence_id
            for item in packet.evidence_items
            if item.role == EvidenceRole.CONTRADICTING
        ]

        unknowns = [
            "No hypothesis-specific evidence has been established."
        ]

        next_check = self._next_checks(key)

        confidence = ConfidenceComponents(
            authority=0.0,
            coverage=0.0,
            agreement=0.0,
            recency=0.0,
        )

        return Hypothesis(
            hypothesis=key,
            evidence_for=supporting,
            evidence_against=contradicting,
            unknowns=unknowns,
            confidence_components=confidence,
            next_check=next_check,
        )

    @staticmethod
    def _next_checks(key: str) -> list[str]:
        checks = {
            "technical_availability": [
                "Check uptime and HTTP availability for the target."
            ],
            "crawl_indexation": [
                "Check crawlability and indexation evidence."
            ],
            "deployment_content_regression": [
                "Check recent deployments and content changes."
            ],
            "serp_intent_feature": [
                "Check recent SERP intent and feature changes."
            ],
            "competitor_improvement": [
                "Check competitor visibility and content changes."
            ],
            "ctr_snippet_regression": [
                "Check CTR and search-result snippet changes."
            ],
            "cannibalization": [
                "Check other pages ranking for the same query."
            ],
            "internal_linking_authority": [
                "Check internal linking and authority changes."
            ],
            "backlink_loss": [
                "Check recent backlink gains and losses."
            ],
            "demand_seasonality": [
                "Check search demand and seasonal patterns."
            ],
            "core_web_vitals": [
                "Check Core Web Vitals and page experience evidence."
            ],
            "measurement_freshness": [
                "Check source freshness and measurement completeness."
            ],
        }

        return checks.get(
            key,
            ["Collect additional evidence for this hypothesis."],
        )