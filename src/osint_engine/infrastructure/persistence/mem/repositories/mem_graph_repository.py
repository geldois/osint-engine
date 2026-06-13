from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.graph_repository import (
    GraphRepository,
)
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.errors.entity_error import NotFoundEntityError

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemGraphRepository(GraphRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.graphs = mem_storage.graphs

    @override
    async def find(self, *, graph_id: UUID) -> Graph | None:
        return self.graphs.get(graph_id, None)

    @override
    async def get(self, *, graph_id: UUID) -> Graph:
        found = await self.find(graph_id=graph_id)

        if found is None:
            raise NotFoundEntityError(entity_id=graph_id, subject=Graph)

        return found

    @override
    async def save(self, *, graph: Graph) -> None:
        if graph.id not in self.graphs:
            self.graphs[graph.id] = graph

    @override
    async def save_many(self, *, graphs: frozenset[Graph]) -> None:
        for graph in graphs:
            await self.save(graph=graph)
