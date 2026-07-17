from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.edge_repository import (
    EdgeRepository,
)
from osint_engine.domain.entities.bases.edge import Edge
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


type EdgeRevision = EntityRevision[Edge[UUID, UUID, UUID]]


class MemEdgeRepository(EdgeRepository):
    @override
    def __init__(
        self,
        *,
        mem_storage: MemStorage,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
    ) -> None:
        self.edges = mem_storage.edges
        self.revision_merge_policy = revision_merge_policy
        self.revision_selection_policy = revision_selection_policy

    @override
    async def _save(self, *, revision: EdgeRevision) -> EdgeRevision:
        edge = revision.entity

        self.edges[edge.id][edge.content_id] = revision

        return revision

    @override
    async def find(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> EdgeRevision | None:
        edge_revisions = self.edges.get(id_)

        if edge_revisions is None:
            return None

        if content_id is not None:
            return edge_revisions.get(content_id)

        return self.revision_selection_policy(edge_revisions.values())

    @override
    async def get(self, *, id_: UUID, content_id: UUID | None = None) -> EdgeRevision:
        found = await self.find(id_=id_, content_id=content_id)

        if found is None:
            raise EntityNotFoundError(entity_id=id_, subject=Edge)

        return found

    @override
    async def merge(self, *, revision: EdgeRevision) -> EdgeRevision:
        found = await self.find(id_=revision.entity.id)

        merged = (
            self.revision_merge_policy(found, revision)
            if found is not None
            else revision
        )

        return await self._save(revision=merged)

    @override
    async def merge_many(self, *, revisions: frozenset[EdgeRevision]) -> None:
        for revision in revisions:
            await self.merge(revision=revision)
