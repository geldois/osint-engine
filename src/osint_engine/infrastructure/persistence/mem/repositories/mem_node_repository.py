from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.node_repository import (
    NodeRepository,
)
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.entity_error import EntityNotFoundError

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


class MemNodeRepository(NodeRepository):
    @override
    def __init__(self, *, mem_storage: MemStorage) -> None:
        self.nodes = mem_storage.nodes

    @override
    async def find(self, *, node_id: UUID) -> Node[UUID] | None:
        return self.nodes.get(node_id, None)

    @override
    async def get(self, *, node_id: UUID) -> Node[UUID]:
        found = await self.find(node_id=node_id)

        if found is None:
            raise EntityNotFoundError(entity_id=node_id, subject=Node)

        return found

    @override
    async def save(self, *, node: Node[UUID]) -> None:
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    @override
    async def save_many(self, *, nodes: frozenset[Node[UUID]]) -> None:
        for node in nodes:
            await self.save(node=node)
