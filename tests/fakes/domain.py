from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

FakeEntityID = NewType("FakeEntityID", UUID)
FakeEdgeID = NewType("FakeEdgeID", UUID)
FakeNodeID = NewType("FakeNodeID", UUID)


def _make_test_namespace(*, name: str) -> EntityNAMESPACE:
    member = object.__new__(EntityNAMESPACE)
    member._name_ = name
    member._value_ = name

    EntityNAMESPACE.__init__(member, name)

    return member


TEST = _make_test_namespace(name="TEST")
TEST_DIFF = _make_test_namespace(name="TEST_DIFF")
TEST_EDGE = _make_test_namespace(name="TEST_EDGE")
TEST_GRAPH = _make_test_namespace(name="TEST_GRAPH")
TEST_MERGEABLE = _make_test_namespace(name="TEST_MERGEABLE")
TEST_NODE = _make_test_namespace(name="TEST_NODE")


class FakeEntity(
    Entity[FakeEntityID], id_fields=frozenset({"content"}), namespace=TEST
):
    content: str

    @override
    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(content=content, **kwargs)


class FakeEdge(
    Edge[FakeEdgeID, UUID, UUID], id_fields=frozenset({"content"}), namespace=TEST_EDGE
):
    content: str

    @override
    def __init__(
        self, *, source_id: UUID, target_id: UUID, content: str, **kwargs: object
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, content=content, **kwargs
        )


class FakeDefaultEdge(
    Edge[FakeEdgeID, UUID, UUID], id_fields=None, namespace=TEST_EDGE
):
    content: str

    @override
    def __init__(
        self, *, source_id: UUID, target_id: UUID, content: str, **kwargs: object
    ) -> None:
        super().__init__(
            source_id=source_id, target_id=target_id, content=content, **kwargs
        )


class FakeNode(Node[FakeNodeID], id_fields=frozenset({"content"}), namespace=TEST_NODE):
    content: str

    @override
    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(content=content, **kwargs)


class FakeMergeableNode(
    Node[FakeNodeID], id_fields=frozenset({"key"}), namespace=TEST_MERGEABLE
):
    key: str
    label: str | None

    @override
    def __init__(self, *, key: str, label: str | None = None, **kwargs: object) -> None:
        super().__init__(key=key, label=label, **kwargs)
