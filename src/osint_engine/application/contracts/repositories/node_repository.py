from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
from uuid import UUID

from osint_engine.application.contracts.repositories.entity_repository import (
    EntityRepository,
)
from osint_engine.domain.entities.bases.node import Node

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision


class NodeRepository(EntityRepository[Node[UUID]]):
    @abstractmethod
    async def list_by_type(
        self, *, node_type: type[Node[UUID]]
    ) -> tuple[EntityRevision[Node[UUID]], ...]:
        raise NotImplementedError
