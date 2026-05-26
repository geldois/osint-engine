from __future__ import annotations

from enum import Enum


class RiskFactor(Enum):
    weight: float

    HAS_LEGAL_PROCEEDINGS = (0.2,)
    HAS_TENDERS_WITH_SHORT_LIFESPAN = (0.3,)

    def __new__(cls, weight: float) -> RiskFactor:
        obj = object.__new__(cls)
        obj.weight = weight

        return obj
