from dataclasses import dataclass


@dataclass(frozen=True)
class PriorityWeights:
    """
    Configurable weights for transparent priority scoring.

    All weights are intentionally explicit so the calculation
    remains reproducible and auditable.
    """

    business_impact: float = 0.25
    search_impact: float = 0.20
    confidence: float = 0.15
    urgency: float = 0.15
    affected_scope: float = 0.10
    effort: float = 0.05
    risk: float = 0.10

    def validate(self) -> None:
        weights = [
            self.business_impact,
            self.search_impact,
            self.confidence,
            self.urgency,
            self.affected_scope,
            self.effort,
            self.risk,
        ]

        if any(weight < 0 for weight in weights):
            raise ValueError("Priority weights cannot be negative.")

        if sum(weights) <= 0:
            raise ValueError("At least one priority weight must be greater than zero.")


@dataclass(frozen=True)
class PriorityResult:
    """
    Transparent priority calculation result.
    """

    score: float
    level: str
    components: dict[str, float]
    weights: dict[str, float]
    version: str


class PriorityScorer:
    """
    Calculates a transparent, reproducible priority score.

    Inputs are normalized to the range 0.0-1.0.

    Higher:
        business impact
        search impact
        confidence
        urgency
        affected scope

    Lower:
        effort
        risk

    The final score is normalized against the configured
    weights so changing the weights does not change the
    expected score range.
    """

    VERSION = "priority-v1"

    def __init__(self, weights: PriorityWeights | None = None):
        self.weights = weights or PriorityWeights()
        self.weights.validate()

    def score(
        self,
        *,
        business_impact: float,
        search_impact: float,
        confidence: float,
        urgency: float,
        affected_scope: float,
        effort: float,
        risk: float,
    ) -> PriorityResult:

        components = {
            "business_impact": self._validate_component(
                "business_impact", business_impact
            ),
            "search_impact": self._validate_component(
                "search_impact", search_impact
            ),
            "confidence": self._validate_component(
                "confidence", confidence
            ),
            "urgency": self._validate_component(
                "urgency", urgency
            ),
            "affected_scope": self._validate_component(
                "affected_scope", affected_scope
            ),
            "effort": self._validate_component(
                "effort", effort
            ),
            "risk": self._validate_component(
                "risk", risk
            ),
        }

        # Effort and risk reduce priority.
        positive_score = (
            components["business_impact"] * self.weights.business_impact
            + components["search_impact"] * self.weights.search_impact
            + components["confidence"] * self.weights.confidence
            + components["urgency"] * self.weights.urgency
            + components["affected_scope"] * self.weights.affected_scope
        )

        negative_score = (
            components["effort"] * self.weights.effort
            + components["risk"] * self.weights.risk
        )

        total_weight = sum(
            [
                self.weights.business_impact,
                self.weights.search_impact,
                self.weights.confidence,
                self.weights.urgency,
                self.weights.affected_scope,
                self.weights.effort,
                self.weights.risk,
            ]
        )

        raw_score = positive_score - negative_score

        # Normalize from [-negative_weight, positive_weight]
        # into [0, 1].
        minimum = -(
            self.weights.effort
            + self.weights.risk
        )

        maximum = (
            self.weights.business_impact
            + self.weights.search_impact
            + self.weights.confidence
            + self.weights.urgency
            + self.weights.affected_scope
        )

        if maximum == minimum:
            normalized_score = 0.0
        else:
            normalized_score = (raw_score - minimum) / (
                maximum - minimum
            )

        normalized_score = max(0.0, min(1.0, normalized_score))

        return PriorityResult(
            score=round(normalized_score, 4),
            level=self._level(normalized_score),
            components=components,
            weights={
                "business_impact": self.weights.business_impact,
                "search_impact": self.weights.search_impact,
                "confidence": self.weights.confidence,
                "urgency": self.weights.urgency,
                "affected_scope": self.weights.affected_scope,
                "effort": self.weights.effort,
                "risk": self.weights.risk,
            },
            version=self.VERSION,
        )

    @staticmethod
    def _validate_component(name: str, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"{name} must be between 0.0 and 1.0."
            )

        return float(value)

    @staticmethod
    def _level(score: float) -> str:
        if score >= 0.75:
            return "high"

        if score >= 0.50:
            return "medium"

        return "low"

