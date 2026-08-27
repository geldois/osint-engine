from __future__ import annotations

from datetime import datetime  # noqa: TC003
from uuid import UUID  # noqa: TC003

from pydantic import BaseModel

from osint_engine.application.consumption.entity_record import (  # noqa: TC001
    ConsumptionOutcome,
)


class EntityRefSchema(BaseModel):
    id: UUID
    content_id: UUID


class EntityRecordSchema(BaseModel):
    id: UUID
    entity_id: UUID
    entity_ref: EntityRefSchema | None
    outcome: ConsumptionOutcome
    provider: str
    requested_at: datetime
    username: str
