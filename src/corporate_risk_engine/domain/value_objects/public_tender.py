from pydantic import BaseModel

from corporate_risk_engine.domain.value_objects.
from corporate_risk_engine.domain.value_objects.money import Money


class PublicTender(BaseModel):
    model_config = {"frozen": True}

    cnae: str
    description: str
    value: Money
