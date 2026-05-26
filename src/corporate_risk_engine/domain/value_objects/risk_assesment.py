from corporate_risk_engine.domain.value_objects.risk_factor import RiskFactor


class RiskAssesment:
    def __init__(self, *, risk_factors: set[RiskFactor]) -> None:
        self.risk_factors = risk_factors
        self.score = self._compute_score()

    def _compute_score(self) -> float:
        score = 0

        for risk_factor in self.risk_factors:
            score += risk_factor.weight

        return score
