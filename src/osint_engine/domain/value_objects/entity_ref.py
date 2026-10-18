from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from osint_engine.domain.errors.entity_error import EntityRefMismatchError

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.entity import Entity


EntityType_co = TypeVar("EntityType_co", bound="Entity[UUID]", covariant=True)
IDType_co = TypeVar("IDType_co", bound=UUID, covariant=True)


@dataclass(eq=True, frozen=True, kw_only=True)
class EntityRef(Generic[EntityType_co, IDType_co]):  # noqa: UP046
    entity_type: type[EntityType_co]
    id: IDType_co
    content_id: IDType_co

    def verify[Entity_: Entity[UUID]](self, *, entity: Entity_) -> Entity_:
        if (
            type(entity) is not self.entity_type
            or entity.id != self.id
            or entity.content_id != self.content_id
        ):
            raise EntityRefMismatchError(
                subject=self.entity_type,
                ref_id=self.id,
                ref_content_id=self.content_id,
                entity_id=entity.id,
                entity_content_id=entity.content_id,
            )

        return entity
