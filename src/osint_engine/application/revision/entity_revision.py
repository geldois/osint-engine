from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from osint_engine.application.errors.revision_error import (
    EmptyProviderError,
    NonUTCAttributeError,
)
from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.domain.value_objects.entity_ref import EntityRef

if TYPE_CHECKING:
    from datetime import datetime

Entity_co = TypeVar("Entity_co", bound=Entity[UUID], covariant=True)


@dataclass(eq=True, frozen=True, kw_only=True)
class EntityRevision(Generic[Entity_co]):  # noqa: UP046
    entity: Entity_co
    fetched_at: datetime
    merged_at: datetime | None
    provider: str

    def __post_init__(self) -> None:
        if self.fetched_at.tzinfo is not UTC:
            raise NonUTCAttributeError(
                attribute="fetched_at", tzinfo=str(self.fetched_at.tzinfo)
            )

        if self.merged_at is not None and self.merged_at.tzinfo is not UTC:
            raise NonUTCAttributeError(
                attribute="merged_at", tzinfo=str(self.merged_at.tzinfo)
            )

        if not self.provider.strip():
            raise EmptyProviderError

    @property
    def ref(self) -> EntityRef:
        return EntityRef(id=self.entity.id, content_id=self.entity.content_id)
