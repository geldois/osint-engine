from dataclasses import FrozenInstanceError
from typing import NewType, override
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.entity import Edge, Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.graph import Graph

FakeEdgeID = NewType("FakeEdgeID", UUID)
FakeNodeID = NewType("FakeNodeID", UUID)


class FakeEdge(Edge[FakeEdgeID], namespace=EntityNAMESPACE.TEST_EDGE):
    content: str

    @override
    def __init__(
        self, *, source_id: UUID, target_id: UUID, content: str, **kwargs: object
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, content=content, **kwargs
        )


class FakeNode(Node[FakeNodeID], namespace=EntityNAMESPACE.TEST_NODE):
    content: str

    @override
    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(content=content, **kwargs)


# INVALID CASES


def test_graph_instances_are_immutable() -> None:
    edges = frozenset({FakeEdge(source_id=uuid4(), target_id=uuid4(), content="test")})
    nodes = frozenset({FakeNode(content="test")})
    graph = Graph(edges=edges, nodes=nodes, root_id=uuid4())

    with pytest.raises(FrozenInstanceError):
        graph.edges = frozenset(  # pyright: ignore[reportAttributeAccessIssue]
            {FakeEdge(source_id=uuid4(), target_id=uuid4(), content="testing...")}
        )

    with pytest.raises(FrozenInstanceError):
        graph.nodes = frozenset({FakeNode(content="testing...")})  # pyright: ignore[reportAttributeAccessIssue]

    with pytest.raises(FrozenInstanceError):
        graph.root_id = uuid4()

    with pytest.raises(FrozenInstanceError):
        del graph.edges

    with pytest.raises(FrozenInstanceError):
        del graph.nodes

    with pytest.raises(FrozenInstanceError):
        del graph.root_id
