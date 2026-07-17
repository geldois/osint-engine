from __future__ import annotations

from typing import TYPE_CHECKING, NewType, cast, override
from uuid import UUID

from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphInconsistentError,
    GraphRootNotInNodesError,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node

GraphID = NewType("GraphID", UUID)


class Graph(
    Entity[GraphID],
    id_fields=frozenset({"edges", "nodes", "root_id"}),
    namespace=EntityNAMESPACE.GRAPH,
):
    edges: frozenset[Edge[UUID, UUID, UUID]]
    nodes: frozenset[Node[UUID]]
    root_id: UUID

    @override
    def __init_subclass__(
        cls,
        *,
        id_fields: frozenset[str] | None,
        namespace: EntityNAMESPACE,
        **kwargs: object,
    ) -> None:
        if id_fields is not None:
            cls.id_fields |= id_fields

        super().__init_subclass__(
            id_fields=cls.id_fields, namespace=namespace, **kwargs
        )

    @override
    def __init__(
        self,
        *,
        edges: frozenset[Edge[UUID, UUID, UUID]],
        nodes: frozenset[Node[UUID]],
        root_id: UUID,
    ) -> None:
        if not nodes:
            raise GraphHasNoNodesError

        if not any(node.id == root_id for node in nodes):
            raise GraphRootNotInNodesError(root_id=root_id)

        node_ids = frozenset({node.id for node in nodes})

        if not all(
            edge.source_id in node_ids and edge.target_id in node_ids for edge in edges
        ):
            raise GraphInconsistentError

        super().__init__(edges=edges, nodes=nodes, root_id=root_id)

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> GraphID:
        edges = cast("frozenset[Edge[UUID, UUID, UUID]]", kwargs["edges"])
        nodes = cast("frozenset[Node[UUID]]", kwargs["nodes"])

        kwargs["edges"] = tuple(sorted(edge.id for edge in edges))
        kwargs["nodes"] = tuple(sorted(node.id for node in nodes))

        return super()._calculate_id(**kwargs)
