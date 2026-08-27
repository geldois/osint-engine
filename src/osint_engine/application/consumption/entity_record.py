from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID

    from osint_engine.domain.value_objects.entity_ref import EntityRef

type ConsumptionOutcome = Literal[
    "already_fetched", "empty", "expanded", "failed", "invalid"
]


@dataclass(eq=True, frozen=True, kw_only=True)
class EntityRecord:
    id: UUID
    entity_id: UUID
    entity_ref: EntityRef | None
    outcome: ConsumptionOutcome
    provider: str
    requested_at: datetime
    username: str
