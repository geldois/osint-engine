from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from osint_engine.application.contracts.repositories.entity_repository import (
    EntityRepository,
)
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision


class GraphRepository(EntityRepository[Graph]):
    @abstractmethod
    async def list_revisions_by_root(
        self, *, root_id: UUID
    ) -> tuple[EntityRevision[Graph], ...]:
        raise NotImplementedError
