from pydantic import BaseModel

from corporate_risk_engine.domain.value_objects.risk_assesment import RiskAssesment


class Enterprise(BaseModel):
    cnpj: str
    razao_social: str
    risk_assesment: RiskAssesment
