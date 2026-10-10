from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.bases.graph import Graph
from tests.fakes.domain import FakeEdge, FakeMergeableNode, FakeNode

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.edge import Edge
    from osint_engine.domain.entities.bases.node import Node

type MakeFakeEdge = Callable[..., FakeEdge]
type MakeFakeNode = Callable[..., FakeNode]
type MakeFakeMergeableNode = Callable[..., FakeMergeableNode]
type MakeGraph = Callable[..., Graph]


@pytest.fixture
def make_fake_edge() -> MakeFakeEdge:

    def fake_edge(
        *,
        source_id: UUID | None = None,
        target_id: UUID | None = None,
        content: str | None = None,
    ) -> FakeEdge:
        return FakeEdge(
            source_id=source_id if source_id is not None else uuid4(),
            target_id=target_id if target_id is not None else uuid4(),
            content=content if content is not None else str(uuid4()),
        )

    return fake_edge


@pytest.fixture
def make_fake_node() -> MakeFakeNode:

    def fake_node(*, content: str | None = None) -> FakeNode:
        return FakeNode(content=content if content is not None else str(uuid4()))

    return fake_node


@pytest.fixture
def make_fake_mergeable_node() -> MakeFakeMergeableNode:

    def fake_mergeable_node(
        *, key: str | None = None, label: str | None = None
    ) -> FakeMergeableNode:
        return FakeMergeableNode(
            key=key if key is not None else str(uuid4()), label=label
        )

    return fake_mergeable_node


@pytest.fixture
def make_graph(make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode) -> MakeGraph:

    def graph(
        *,
        edges: Iterable[Edge[UUID, UUID, UUID]] | None = None,
        nodes: Iterable[Node[UUID]] | None = None,
        root_id: UUID | None = None,
    ) -> Graph:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)

        return Graph(
            edges=frozenset(edges) if edges is not None else frozenset({edge}),
            nodes=frozenset(nodes)
            if nodes is not None
            else frozenset({node_a, node_b}),
            root_id=root_id if root_id is not None else node_a.id,
        )

    return graph
