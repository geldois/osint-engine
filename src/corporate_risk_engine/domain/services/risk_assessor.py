from corporate_risk_engine.domain.value_objects.risk_assesment import RiskAssesment
from corporate_risk_engine.domain.value_objects.risk_factor import RiskFactor


def risk_assessor(*, risk_factors: set[RiskFactor]) -> RiskAssesment:
    return RiskAssesment(risk_factors=risk_factors)
