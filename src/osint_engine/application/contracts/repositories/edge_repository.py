from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge


class EdgeRepository(ABC):
    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    async def find(self, *, edge_id: UUID) -> Edge[UUID] | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *, edge_id: UUID) -> Edge[UUID]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, *, edge: Edge[UUID]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_many(self, *, edges: frozenset[Edge[UUID]]) -> None:
        raise NotImplementedError
