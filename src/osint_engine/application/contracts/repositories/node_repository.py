from abc import ABC, abstractmethod
from uuid import UUID

from osint_engine.domain.entities.entity import Node


class NodeRepository(ABC):
    @abstractmethod
    async def find[IDType: UUID](self, *, node_id: UUID) -> Node[IDType] | None:
        raise NotImplementedError

    @abstractmethod
    async def get[IDType: UUID](self, *, node_id: UUID) -> Node[IDType]:
        raise NotImplementedError

    @abstractmethod
    async def merge[IDType: UUID](self, *, node: Node[IDType]) -> None:
        raise NotImplementedError
