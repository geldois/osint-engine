from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node


class NodeRepository(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find(self, *, node_id: UUID) -> Node[UUID] | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *, node_id: UUID) -> Node[UUID]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, *, node: Node[UUID]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_many(self, *, nodes: frozenset[Node[UUID]]) -> None:
        raise NotImplementedError
