from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.graph_repository import (
    GraphRepository,
)
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.errors.entity_error import EntityNotFoundError

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


type GraphRevision = EntityRevision[Graph]


class MemGraphRepository(GraphRepository):
    @override
    def __init__(
        self,
        *,
        mem_storage: MemStorage,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> None:
        self.graphs = mem_storage.graphs
        self.revision_merge_policy = revision_merge_policy
        self.revision_selection_policy = revision_selection_policy

    @override
    async def _save(self, *, revision: GraphRevision) -> GraphRevision:
        graph = revision.entity

        self.graphs[graph.id][graph.content_id] = revision

        return revision

    @override
    async def find(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> GraphRevision | None:
        graph_revisions = self.graphs.get(id_)

        if graph_revisions is None:
            return None

        if content_id is not None:
            return graph_revisions.get(content_id)

        return self.revision_selection_policy(graph_revisions.values())

    @override
    async def get(self, *, id_: UUID, content_id: UUID | None = None) -> GraphRevision:
        found = await self.find(id_=id_, content_id=content_id)

        if found is None:
            raise EntityNotFoundError(entity_id=id_, subject=Graph)

        return found

    @override
    async def merge(self, *, revision: GraphRevision) -> GraphRevision:
        found = await self.find(id_=revision.entity.id)

        merged = (
            self.revision_merge_policy(found, revision)
            if found is not None
            else revision
        )

        return await self._save(revision=merged)

    @override
    async def merge_many(self, *, revisions: frozenset[GraphRevision]) -> None:
        for revision in revisions:
            await self.merge(revision=revision)
