from datetime import date

from pydantic import BaseModel

from corporate_risk_engine.domain.entities.partner import Partner
from corporate_risk_engine.domain.value_objects.money import Money
from corporate_risk_engine.domain.value_objects.public_tender import PublicTender


class Company(BaseModel):
    cnae: str
    cnpj: str
    date: date
    name: str
    partners: set[Partner]
    public_tenders: set[PublicTender]
    share_capital: Money
