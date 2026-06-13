from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.edge_repository import (
    EdgeRepository,
)
from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.errors.entity_error import NotFoundEntityError

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemEdgeRepository(EdgeRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.edges = mem_storage.edges

    @override
    async def find(self, *, edge_id: UUID) -> Edge[UUID] | None:
        return self.edges.get(edge_id, None)

    @override
    async def get(self, *, edge_id: UUID) -> Edge[UUID]:
        found = await self.find(edge_id=edge_id)

        if found is None:
            raise NotFoundEntityError(entity_id=edge_id, subject=Edge)

        return found

    @override
    async def save(self, *, edge: Edge[UUID]) -> None:
        if edge.id not in self.edges:
            self.edges[edge.id] = edge

    @override
    async def save_many(self, *, edges: frozenset[Edge[UUID]]) -> None:
        for edge in edges:
            await self.save(edge=edge)
