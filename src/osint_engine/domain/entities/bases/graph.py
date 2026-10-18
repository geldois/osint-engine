from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, NewType, cast, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphRootNotInNodesError,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node
    from osint_engine.domain.value_objects.entity_ref import EntityRef

GraphID = NewType("GraphID", UUID)

type _EdgeLike = Edge[UUID, UUID, UUID] | EntityRef[Edge[UUID, UUID, UUID], UUID]
type _NodeLike = Node[UUID] | EntityRef[Node[UUID], UUID]


class Graph[
    EdgeType: Edge[UUID, UUID, UUID] | EntityRef[Edge[UUID, UUID, UUID], UUID],
    NodeType: Node[UUID] | EntityRef[Node[UUID], UUID],
](
    Entity[GraphID],
    id_fields=frozenset({"edges", "nodes", "root_id"}),
    namespace=EntityNAMESPACE.GRAPH,
):
    edges: frozenset[EdgeType]
    nodes: frozenset[NodeType]
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

    @abstractmethod
    @override
    def __init__(
        self, *, edges: frozenset[EdgeType], nodes: frozenset[NodeType], root_id: UUID
    ) -> None:
        if not nodes:
            raise GraphHasNoNodesError

        if not any(node.id == root_id for node in nodes):
            raise GraphRootNotInNodesError(root_id=root_id)

        super().__init__(edges=edges, nodes=nodes, root_id=root_id)

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> GraphID:
        for_content = bool(kwargs.get("for_content"))
        edges = cast("frozenset[_EdgeLike]", kwargs["edges"])
        nodes = cast("frozenset[_NodeLike]", kwargs["nodes"])

        if for_content:
            kwargs["edges"] = tuple(sorted(edge.content_id for edge in edges))
            kwargs["nodes"] = tuple(sorted(node.content_id for node in nodes))
        else:
            kwargs["edges"] = tuple(sorted(edge.id for edge in edges))
            kwargs["nodes"] = tuple(sorted(node.id for node in nodes))

        return super()._calculate_id(**kwargs)
