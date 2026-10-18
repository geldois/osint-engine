from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.repositories.graph_repository import (
    GraphRepository,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.graphs import CompositeGraph, FlattenedGraph, Graph
from osint_engine.domain.errors.entity_error import EntityNotFoundError

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.contracts.repositories.edge_repository import (
        EdgeRepository,
    )
    from osint_engine.application.contracts.repositories.node_repository import (
        NodeRepository,
    )
    from osint_engine.application.revision.policies.revision_merge_policy import (
        RevisionMergePolicy,
    )
    from osint_engine.application.revision.policies.revision_selection_policy import (
        RevisionSelectionPolicy,
    )
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage


type CompositeGraphRevision = EntityRevision[CompositeGraph]
type FlattenedGraphRevision = EntityRevision[FlattenedGraph]


class MemGraphRepository(GraphRepository):
    @override
    def __init__(
        self,
        *,
        mem_storage: MemStorage,
        revision_merge_policy: RevisionMergePolicy,
        revision_selection_policy: RevisionSelectionPolicy,
        edge_repository: EdgeRepository,
        node_repository: NodeRepository,
    ) -> None:
        self.graphs = mem_storage.graphs
        self.revision_merge_policy = revision_merge_policy
        self.revision_selection_policy = revision_selection_policy
        self._edge_repository = edge_repository
        self._node_repository = node_repository

    @override
    async def _compose_graph(
        self, *, flattened_graph: FlattenedGraph
    ) -> CompositeGraph:
        edge_id_pairs = tuple(
            [(edge_ref.id, edge_ref.content_id) for edge_ref in flattened_graph.edges]
        )
        node_id_pairs = tuple(
            [(node_ref.id, node_ref.content_id) for node_ref in flattened_graph.nodes]
        )

        edge_revisions = await self._edge_repository.get_many(id_pairs=edge_id_pairs)
        node_revisions = await self._node_repository.get_many(id_pairs=node_id_pairs)

        edges = frozenset(edge_revision.entity for edge_revision in edge_revisions)
        nodes = frozenset(node_revision.entity for node_revision in node_revisions)

        root_id = flattened_graph.root_id

        return CompositeGraph(edges=edges, nodes=nodes, root_id=root_id)

    @override
    async def _compose_graph_revision(
        self, *, flattened_graph_revision: FlattenedGraphRevision
    ) -> CompositeGraphRevision:
        return EntityRevision(
            entity=await self._compose_graph(
                flattened_graph=flattened_graph_revision.entity
            ),
            fetched_at=flattened_graph_revision.fetched_at,
            merged_at=flattened_graph_revision.merged_at,
            provider=flattened_graph_revision.provider,
        )

    @override
    def _flatten_graph_revision(
        self, *, composite_graph_revision: CompositeGraphRevision
    ) -> FlattenedGraphRevision:
        return EntityRevision(
            entity=composite_graph_revision.entity.flatten(),
            fetched_at=composite_graph_revision.fetched_at,
            merged_at=composite_graph_revision.merged_at,
            provider=composite_graph_revision.provider,
        )

    @override
    async def _save(
        self, *, revision: CompositeGraphRevision
    ) -> CompositeGraphRevision:
        graph = revision.entity

        flattened_graph_revision = self._flatten_graph_revision(
            composite_graph_revision=revision
        )

        self.graphs[graph.id][graph.content_id] = flattened_graph_revision

        return revision

    @override
    async def find(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> CompositeGraphRevision | None:
        flattened_graph_revisions = self.graphs.get(id_)

        if flattened_graph_revisions is None:
            return None

        if content_id is not None:
            flattened_graph_revision = flattened_graph_revisions.get(content_id)

            return (
                await self._compose_graph_revision(
                    flattened_graph_revision=flattened_graph_revision
                )
                if flattened_graph_revision is not None
                else None
            )

        return self.revision_selection_policy(
            tuple(
                [
                    await self._compose_graph_revision(
                        flattened_graph_revision=flattened_graph_revision
                    )
                    for flattened_graph_revision in flattened_graph_revisions.values()
                ]
            )
        )

    @override
    async def get(
        self, *, id_: UUID, content_id: UUID | None = None
    ) -> CompositeGraphRevision:
        found = await self.find(id_=id_, content_id=content_id)

        if found is None:
            raise EntityNotFoundError(entity_id=id_, subject=Graph)

        return found

    @override
    async def merge(
        self, *, revision: CompositeGraphRevision
    ) -> CompositeGraphRevision:
        found = await self.find(id_=revision.entity.id)

        merged = (
            self.revision_merge_policy(found, revision)
            if found is not None
            else revision
        )

        graph = merged.entity

        new_node_revisions: set[EntityRevision[Node[UUID]]] = set()

        for node in graph.nodes:
            existing = await self._node_repository.find(
                id_=node.id, content_id=node.content_id
            )

            if existing is None:
                new_node_revisions.add(
                    EntityRevision(
                        entity=node,
                        fetched_at=merged.fetched_at,
                        merged_at=merged.merged_at,
                        provider=merged.provider,
                    )
                )

        if new_node_revisions:
            await self._node_repository.merge_many(
                revisions=frozenset(new_node_revisions)
            )

        new_edge_revisions: set[EntityRevision[Edge[UUID, UUID, UUID]]] = set()

        for edge in graph.edges:
            existing = await self._edge_repository.find(
                id_=edge.id, content_id=edge.content_id
            )

            if existing is None:
                new_edge_revisions.add(
                    EntityRevision(
                        entity=edge,
                        fetched_at=merged.fetched_at,
                        merged_at=merged.merged_at,
                        provider=merged.provider,
                    )
                )

        if new_edge_revisions:
            await self._edge_repository.merge_many(
                revisions=frozenset(new_edge_revisions)
            )

        return await self._save(revision=merged)

    @override
    async def list_revisions(self, *, id_: UUID) -> tuple[CompositeGraphRevision, ...]:
        return tuple(
            [
                await self._compose_graph_revision(
                    flattened_graph_revision=flattened_graph_revision
                )
                for flattened_graph_revision in self.graphs.get(id_, {}).values()
            ]
        )

    @override
    async def list_revisions_by_root(
        self, *, root_id: UUID
    ) -> tuple[CompositeGraphRevision, ...]:
        return tuple(
            [
                await self._compose_graph_revision(
                    flattened_graph_revision=flattened_graph_revision
                )
                for flattened_graph_revisions in self.graphs.values()
                for flattened_graph_revision in flattened_graph_revisions.values()
                if flattened_graph_revision.entity.root_id == root_id
            ]
        )

    @override
    async def list_all_revisions(self) -> tuple[CompositeGraphRevision, ...]:
        return tuple(
            [
                await self._compose_graph_revision(
                    flattened_graph_revision=flattened_graph_revision
                )
                for flattened_graph_revisions in self.graphs.values()
                for flattened_graph_revision in flattened_graph_revisions.values()
            ]
        )
