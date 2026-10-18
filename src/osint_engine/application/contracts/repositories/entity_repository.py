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

    async def find_many(
        self, *, id_pairs: tuple[tuple[UUID, UUID | None], ...]
    ) -> tuple[EntityRevision[Entity_] | None, ...]:
        return tuple(
            [
                await self.find(id_=id_pair[0], content_id=id_pair[1])
                for id_pair in id_pairs
            ]
        )

    @abstractmethod
    async def get(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> EntityRevision[Entity_]:
        raise NotImplementedError

    async def get_many(
        self, *, id_pairs: tuple[tuple[UUID, UUID | None], ...]
    ) -> tuple[EntityRevision[Entity_], ...]:
        return tuple(
            [
                await self.get(id_=id_pair[0], content_id=id_pair[1])
                for id_pair in id_pairs
            ]
        )

    @abstractmethod
    async def merge(
        self, *, revision: EntityRevision[Entity_]
    ) -> EntityRevision[Entity_]:
        raise NotImplementedError

    async def merge_many(
        self, *, revisions: frozenset[EntityRevision[Entity_]]
    ) -> None:
        for revision in revisions:
            await self.merge(revision=revision)

    @abstractmethod
    async def list_revisions(self, *, id_: UUID) -> tuple[EntityRevision[Entity_], ...]:
        raise NotImplementedError
