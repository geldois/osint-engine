from abc import ABC, abstractmethod
from uuid import UUID

from osint_engine.domain.entities.entity import Edge


class EdgeRepository(ABC):
    @abstractmethod
    async def find[IDType: UUID](self, *, edge_id: UUID) -> Edge[IDType] | None:
        raise NotImplementedError

    @abstractmethod
    async def get[IDType: UUID](self, *, edge_id: UUID) -> Edge[IDType]:
        raise NotImplementedError

    @abstractmethod
    async def merge[IDType: UUID](self, *, edge: Edge[IDType]) -> None:
        raise NotImplementedError
