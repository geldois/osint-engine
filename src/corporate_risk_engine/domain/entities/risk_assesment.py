from datetime import UTC, datetime

from pydantic import AwareDatetime, BaseModel, Field, model_validator

from corporate_risk_engine.domain.entities.company import Company
from corporate_risk_engine.domain.value_objects.risk_factor import RiskFactor


class RiskAssesment(BaseModel):
    model_config = {"frozen": True}

    assessed_at: AwareDatetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    company: Company
    is_high_risk: bool
    risk_factors: set[RiskFactor]
    score: float = 0.0

    @model_validator(mode="after")
    def compute_score(self):
        for risk_factor in self.risk_factors:
            self.score += risk_factor.weight

        return self
