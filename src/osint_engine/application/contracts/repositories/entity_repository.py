from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from osint_engine.domain.entities.bases.entity import Entity

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision


class EntityRepository[Entity_: Entity[UUID]](ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _save(
        self, *, revision: EntityRevision[Entity_]
    ) -> EntityRevision[Entity_]:
        raise NotImplementedError

    @abstractmethod
    async def find(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> EntityRevision[Entity_] | None:
        raise NotImplementedError

    @abstractmethod
    async def get(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> EntityRevision[Entity_]:
        raise NotImplementedError

    @abstractmethod
    async def merge(
        self, *, revision: EntityRevision[Entity_]
    ) -> EntityRevision[Entity_]:
        raise NotImplementedError

    @abstractmethod
    async def merge_many(
        self, *, revisions: frozenset[EntityRevision[Entity_]]
    ) -> None:
        raise NotImplementedError
