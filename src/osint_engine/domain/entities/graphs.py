from __future__ import annotations

from typing import override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.graph_error import (
    GraphBrokenInversionError,
    GraphDuplicateEntityError,
    GraphInconsistentError,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.entity_ref import EntityRef


class CompositeGraph(
    Graph[Edge[UUID, UUID, UUID], Node[UUID]],
    id_fields=None,
    namespace=EntityNAMESPACE.GRAPH,
):
    @override
    def __init__(
        self,
        *,
        edges: frozenset[Edge[UUID, UUID, UUID]],
        nodes: frozenset[Node[UUID]],
        root_id: UUID,
    ) -> None:
        edges |= self._collect_inverses(edges)

        node_ids = frozenset({node.id for node in nodes})

        if not all(
            edge.source_id in node_ids and edge.target_id in node_ids for edge in edges
        ):
            raise GraphInconsistentError

        super().__init__(edges=edges, nodes=nodes, root_id=root_id)

    @staticmethod
    def _collect_inverses(
        edges: frozenset[Edge[UUID, UUID, UUID]], /
    ) -> frozenset[Edge[UUID, UUID, UUID]]:
        inverses: set[Edge[UUID, UUID, UUID]] = set()

        for edge in edges:
            inverse = edge.invert()

            if inverse is None:
                continue

            if inverse.invert() != edge:
                raise GraphBrokenInversionError(edge_id=edge.id)

            inverses.add(inverse)

        return frozenset(inverses)

    def merge(self, *, other: CompositeGraph) -> CompositeGraph:
        return CompositeGraph(
            edges=self.edges | other.edges,
            nodes=self.nodes | other.nodes,
            root_id=self.root_id,
        )

    def flatten(self) -> FlattenedGraph:
        return FlattenedGraph(
            edges=frozenset(edge.ref for edge in self.edges),
            nodes=frozenset(node.ref for node in self.nodes),
            root_id=self.root_id,
        )


class FlattenedGraph(
    Graph[EntityRef[Edge[UUID, UUID, UUID], UUID], EntityRef[Node[UUID], UUID]],
    id_fields=None,
    namespace=EntityNAMESPACE.GRAPH,
):
    @override
    def __init__(
        self,
        *,
        edges: frozenset[EntityRef[Edge[UUID, UUID, UUID], UUID]],
        nodes: frozenset[EntityRef[Node[UUID], UUID]],
        root_id: UUID,
    ) -> None:
        for refs in (nodes, edges):
            seen: set[UUID] = set()

            for ref in refs:
                if ref.id in seen:
                    raise GraphDuplicateEntityError(entity_id=ref.id)

                seen.add(ref.id)

        super().__init__(edges=edges, nodes=nodes, root_id=root_id)
