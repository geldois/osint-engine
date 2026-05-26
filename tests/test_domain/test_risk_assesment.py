from corporate_risk_engine.domain.value_objects.risk_assesment import RiskAssesment
from corporate_risk_engine.domain.value_objects.risk_factor import RiskFactor

# VALID CASES


def test_risk_assesment_computes_score() -> None:
    risk_factors = {
        RiskFactor.HAS_LEGAL_PROCEEDINGS,
        RiskFactor.HAS_TENDERS_WITH_SHORT_LIFESPAN,
    }
    risk_assesment = RiskAssesment(risk_factors=risk_factors)

    score = 0

    for risk_factor in risk_factors:
        score += risk_factor.weight

    assert risk_assesment.score == score
