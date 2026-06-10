from abc import ABC, abstractmethod
from uuid import UUID

from osint_engine.domain.value_objects.graph import Graph


class GraphRepository(ABC):
    @abstractmethod
    async def find(self, *, root_id: UUID) -> Graph | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *, root_id: UUID) -> Graph:
        raise NotImplementedError

    @abstractmethod
    async def merge(self, *, graph: Graph) -> None:
        raise NotImplementedError
