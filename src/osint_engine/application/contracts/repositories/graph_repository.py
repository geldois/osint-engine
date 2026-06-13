from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.graph import Graph


class GraphRepository(ABC):
    @abstractmethod
    def __init__(self) -> None: ...

    @abstractmethod
    async def find(self, *, graph_id: UUID) -> Graph | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *, graph_id: UUID) -> Graph:
        raise NotImplementedError

    @abstractmethod
    async def save(self, *, graph: Graph) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_many(self, *, graphs: frozenset[Graph]) -> None:
        raise NotImplementedError
