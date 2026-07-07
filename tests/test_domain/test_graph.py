from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from hypothesis import HealthCheck, given, settings, strategies

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.graph_error import (
    GraphHasNoNodesError,
    GraphInconsistentError,
    GraphRootNotInNodesError,
)

if TYPE_CHECKING:
    from hypothesis.strategies import DataObject

    from tests.conftest import MakeFakeEdge, MakeFakeNode


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


class TestGraphValidation:
    def test_raises_with_empty_node_set(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()

        with pytest.raises(GraphHasNoNodesError):
            Graph(edges=frozenset(), nodes=frozenset(), root_id=node.id)

    def test_raises_when_root_is_absent_from_nodes(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()

        with pytest.raises(GraphRootNotInNodesError):
            Graph(edges=frozenset(), nodes=frozenset({node}), root_id=uuid4())

    def test_raises_when_edge_references_unknown_node(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()
        nonexistent_id = uuid4()
        edge = make_fake_edge(source_id=nonexistent_id, target_id=node.id)

        with pytest.raises(GraphInconsistentError):
            Graph(edges=frozenset({edge}), nodes=frozenset({node}), root_id=node.id)
