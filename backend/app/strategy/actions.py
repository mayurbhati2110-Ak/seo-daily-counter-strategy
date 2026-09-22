from app.models.action import ActionRecommendation, ApprovalState
from app.models.hypothesis import Hypothesis


class ActionStrategy:
    """
    Converts diagnosed SEO hypotheses into deterministic,
    structured action recommendations.

    This layer does not execute changes.
    It only proposes actions for human approval.
    """

    VERSION = "action-strategy-v1"

    def generate(
        self,
        incident_id: str,
        hypotheses: list[Hypothesis],
        target: str | None = None,
    ) -> list[ActionRecommendation]:
        recommendations: list[ActionRecommendation] = []

        for index, hypothesis in enumerate(hypotheses, start=1):
            action = self._build_action(
                incident_id=incident_id,
                hypothesis=hypothesis,
                target=target,
                index=index,
            )

            if action:
                recommendations.append(action)

        return recommendations

    def _build_action(
        self,
        incident_id: str,
        hypothesis: Hypothesis,
        target: str | None,
        index: int,
    ) -> ActionRecommendation | None:

        action_map = {
            "ctr_snippet_regression": {
                "action_type": "review_snippet",
                "why_now": (
                    "Search performance indicates a CTR regression "
                    "for the affected target."
                ),
                "expected_effect": (
                    "Improve organic click-through rate by reviewing "
                    "the title and meta description against the current search intent."
                ),
                "business_value": (
                    "Recover qualified organic traffic without requiring "
                    "ranking improvement."
                ),
                "effort": "low",
                "risk": "low",
                "owner_type": "seo",
                "prerequisites": [
                    "Verify the current SERP snippet.",
                    "Confirm the target query and search intent.",
                ],
                "verification_plan": (
                    "Record the current title and meta description. "
                    "Monitor CTR for the affected query and page, then "
                    "compare against the pre-change baseline using a "
                    "like-for-like window."
                ),
                "rollback": (
                    "Restore the previous title and meta description "
                    "if CTR or relevant business metrics regress."
                ),
            },
            "technical_availability": {
                "action_type": "investigate_availability",
                "why_now": (
                    "Availability issues can directly prevent users "
                    "and search engines from accessing the target."
                ),
                "expected_effect": (
                    "Restore reliable access to the affected target "
                    "if an availability issue is confirmed."
                ),
                "business_value": (
                    "Protect organic traffic and downstream conversions "
                    "from accessibility loss."
                ),
                "effort": "medium",
                "risk": "low",
                "owner_type": "engineering",
                "prerequisites": [
                    "Verify the availability incident.",
                    "Review uptime and server evidence.",
                ],
                "verification_plan": (
                    "Confirm successful responses from the target, "
                    "monitor availability after remediation, and "
                    "re-measure search performance after the verification window."
                ),
                "rollback": (
                    "Revert the infrastructure or configuration change "
                    "that introduced the availability regression."
                ),
            },
            "crawl_indexation": {
                "action_type": "verify_indexation",
                "why_now": (
                    "Search-performance changes warrant verification "
                    "of crawl and indexation status."
                ),
                "expected_effect": (
                    "Identify and remediate a confirmed crawl or "
                    "indexation issue."
                ),
                "business_value": (
                    "Protect eligible search visibility for the affected target."
                ),
                "effort": "medium",
                "risk": "low",
                "owner_type": "seo",
                "prerequisites": [
                    "Check the target URL's indexation status.",
                    "Review crawl errors and indexing signals.",
                ],
                "verification_plan": (
                    "Confirm indexation status after remediation and "
                    "monitor impressions and clicks for the affected target."
                ),
                "rollback": (
                    "Revert only the confirmed indexation-related "
                    "change if it produces a negative result."
                ),
            },
            "competitor_improvement": {
                "action_type": "competitor_analysis",
                "why_now": (
                    "The observed ranking change requires verification "
                    "of competing pages before selecting a response."
                ),
                "expected_effect": (
                    "Identify measurable competitor changes that "
                    "explain the ranking movement."
                ),
                "business_value": (
                    "Focus future optimization on verified "
                    "search-result differences."
                ),
                "effort": "medium",
                "risk": "low",
                "owner_type": "seo",
                "prerequisites": [
                    "Collect competitor ranking evidence.",
                    "Compare competing pages for the affected query.",
                ],
                "verification_plan": (
                    "Document competitor ranking and content changes, "
                    "compare findings with the affected target, and use "
                    "the findings to determine whether a subsequent "
                    "optimization is justified."
                ),
                "rollback": (
                    "No production change is required for this "
                    "investigative action."
                ),
            },
        }

        definition = action_map.get(hypothesis.hypothesis)

        if not definition:
            return None

        confidence = self._confidence_label(
            hypothesis.confidence_components.coverage
        )

        return ActionRecommendation(
            action_id=f"{self.VERSION}:{incident_id}:{index}",
            incident_id=incident_id,
            action_type=definition["action_type"],
            target=target,
            why_now=definition["why_now"],
            expected_effect=definition["expected_effect"],
            confidence=confidence,
            business_value=definition["business_value"],
            effort=definition["effort"],
            risk=definition["risk"],
            prerequisites=definition["prerequisites"],
            owner_type=definition["owner_type"],
            verification_plan=definition["verification_plan"],
            rollback=definition["rollback"],
            approval_state=ApprovalState.PENDING,
        )

    @staticmethod
    def _confidence_label(score: float) -> str:
        if score >= 0.8:
            return "high"

        if score >= 0.5:
            return "medium"

        return "low"

