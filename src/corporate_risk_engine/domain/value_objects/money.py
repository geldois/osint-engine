from decimal import Decimal

from pydantic import BaseModel


class Money(BaseModel):
    model_config = {"frozen": True}

    currency: str = "R$"
    value: Decimal
