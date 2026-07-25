from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from hypothesis import HealthCheck, given, settings, strategies

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphInconsistentError,
    GraphRootNotInNodesError,
)
from tests.fakes.domain import TEST_NODE, FakeDefaultEdge, FakeNodeID

if TYPE_CHECKING:
    from hypothesis.strategies import DataObject

    from tests.conftest import MakeFakeEdge, MakeFakeNode

# TEST DOUBLES


class FakeNodeWithContentIdentity(
    Node[FakeNodeID], id_fields=frozenset({"content"}), namespace=TEST_NODE
):
    content: str
    extra_field: str

    def __init__(
        self,
        *,
        content: str,
        extra_field: str,
        **kwargs: object,
    ) -> None:
        super().__init__(
            content=content,
            extra_field=extra_field,
            **kwargs,
        )


class TestGraphSubclassContract:
    def test_graph_inherits_directly_from_entity(self) -> None:
        bases = Graph.__bases__

        assert Entity in bases

        assert Edge not in bases

        assert Node not in bases

    def test_edges_and_nodes_are_annotated_as_frozenset(self) -> None:
        annotations = Graph.__annotations__
        contract = "frozenset"

        assert annotations["edges"].startswith(contract)

        assert annotations["nodes"].startswith(contract)

    def test_edges_and_nodes_are_frozenset_at_runtime(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()

        graph = Graph(edges=frozenset(), nodes=frozenset({node}), root_id=node.id)

        assert isinstance(graph.edges, frozenset)

        assert isinstance(graph.nodes, frozenset)

    def test_graph_id_is_not_none(self, make_fake_node: MakeFakeNode) -> None:
        node = make_fake_node()

        graph = Graph(edges=frozenset(), nodes=frozenset({node}), root_id=node.id)

        assert graph.id is not None


class TestGraphIdentity:
    @given(data=strategies.data())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_id_is_stable_under_element_permutations(
        self,
        data: DataObject,
        make_fake_edge: MakeFakeEdge,
        make_fake_node: MakeFakeNode,
    ) -> None:
        nodes = [make_fake_node(content=f"node_{char}") for char in ("a", "b", "c")]
        edges = [
            make_fake_edge(source_id=nodes[0].id, target_id=nodes[1].id),
            make_fake_edge(source_id=nodes[1].id, target_id=nodes[2].id),
        ]
        root = nodes[0]

        node_perm: list[Node[UUID]] = data.draw(strategies.permutations(nodes))
        edge_perm: list[Edge[UUID, UUID, UUID]] = data.draw(
            strategies.permutations(edges)
        )

        id_canonical = Graph._calculate_id(edges=edges, nodes=nodes, root_id=root.id)  # pyright: ignore[reportPrivateUsage]
        id_permuted = Graph._calculate_id(  # pyright: ignore[reportPrivateUsage]
            edges=edge_perm, nodes=node_perm, root_id=root.id
        )

        assert id_canonical == id_permuted

    def test_graph_id_ignores_node_content_id_divergence(self) -> None:
        node_a = FakeNodeWithContentIdentity(content="root", extra_field="value_a")
        node_b = FakeNodeWithContentIdentity(content="root", extra_field="value_b")

        assert node_a.id == node_b.id

        assert node_a.content_id != node_b.content_id

        graph_a = Graph(edges=frozenset(), nodes=frozenset({node_a}), root_id=node_a.id)
        graph_b = Graph(edges=frozenset(), nodes=frozenset({node_b}), root_id=node_b.id)

        assert graph_a.id == graph_b.id

    def test_graph_id_ignores_edge_content_id_divergence(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node_x = make_fake_node()
        node_y = make_fake_node()

        edge_a = FakeDefaultEdge(
            source_id=node_x.id, target_id=node_y.id, content="content_a"
        )
        edge_b = FakeDefaultEdge(
            source_id=node_x.id, target_id=node_y.id, content="content_b"
        )

        assert edge_a.id == edge_b.id

        assert edge_a.content_id != edge_b.content_id

        graph_a = Graph(
            edges=frozenset({edge_a}),
            nodes=frozenset({node_x, node_y}),
            root_id=node_x.id,
        )
        graph_b = Graph(
            edges=frozenset({edge_b}),
            nodes=frozenset({node_x, node_y}),
            root_id=node_x.id,
        )

        assert graph_a.id == graph_b.id


class TestGraphValidation:
    def test_raises_with_empty_node_set(self, make_fake_node: MakeFakeNode) -> None:
        node = make_fake_node()

        with pytest.raises(GraphHasNoNodesError):
            Graph(edges=frozenset(), nodes=frozenset(), root_id=node.id)

    def test_raises_when_root_is_absent_from_nodes(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()
        root_id = uuid4()

        with pytest.raises(GraphRootNotInNodesError) as exception:
            Graph(edges=frozenset(), nodes=frozenset({node}), root_id=root_id)

        assert str(root_id) in str(exception.value)

    def test_raises_when_edge_references_unknown_node(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()
        nonexistent_id = uuid4()
        edge = make_fake_edge(source_id=nonexistent_id, target_id=node.id)

        with pytest.raises(GraphInconsistentError):
            Graph(edges=frozenset({edge}), nodes=frozenset({node}), root_id=node.id)
