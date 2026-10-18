from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from osint_engine.application.contracts.repositories.entity_repository import (
    EntityRepository,
)
from osint_engine.domain.entities.graphs import CompositeGraph, FlattenedGraph

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision


class GraphRepository(EntityRepository[CompositeGraph]):
    @abstractmethod
    async def _compose_graph(
        self, *, flattened_graph: FlattenedGraph
    ) -> CompositeGraph:
        raise NotImplementedError

    @abstractmethod
    async def _compose_graph_revision(
        self, *, flattened_graph_revision: EntityRevision[FlattenedGraph]
    ) -> EntityRevision[CompositeGraph]:
        raise NotImplementedError

    @abstractmethod
    def _flatten_graph_revision(
        self, *, composite_graph_revision: EntityRevision[CompositeGraph]
    ) -> EntityRevision[FlattenedGraph]:
        raise NotImplementedError

    @abstractmethod
    async def list_revisions_by_root(
        self, *, root_id: UUID
    ) -> tuple[EntityRevision[CompositeGraph], ...]:
        raise NotImplementedError

    @abstractmethod
    async def list_all_revisions(self) -> tuple[EntityRevision[CompositeGraph], ...]:
        raise NotImplementedError
