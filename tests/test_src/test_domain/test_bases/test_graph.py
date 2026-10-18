from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

import pytest
from hypothesis import HealthCheck, given, settings, strategies

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.bases.entity import Entity
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.entities.graphs import CompositeGraph, FlattenedGraph
from osint_engine.domain.errors.graph_error import (
    GraphBrokenInversionError,
    GraphDuplicateEntityError,
    GraphHasNoNodesError,
    GraphInconsistentError,
    GraphRootNotInNodesError,
)
from osint_engine.domain.value_objects.entity_ref import EntityRef
from tests.fakes.domain import (
    TEST_NODE,
    FakeDefaultEdge,
    FakeNodeID,
    FakeOneWayEdge,
    FakeVersionedEdge,
)

if TYPE_CHECKING:
    from hypothesis.strategies import DataObject

    from tests.fixtures.domain import MakeFakeEdge, MakeFakeNode


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

        graph = CompositeGraph(
            edges=frozenset(), nodes=frozenset({node}), root_id=node.id
        )

        assert isinstance(graph.edges, frozenset)

        assert isinstance(graph.nodes, frozenset)

    def test_graph_id_is_not_none(self, make_fake_node: MakeFakeNode) -> None:
        node = make_fake_node()

        graph = CompositeGraph(
            edges=frozenset(), nodes=frozenset({node}), root_id=node.id
        )

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

        graph_a = CompositeGraph(
            edges=frozenset(), nodes=frozenset({node_a}), root_id=node_a.id
        )
        graph_b = CompositeGraph(
            edges=frozenset(), nodes=frozenset({node_b}), root_id=node_b.id
        )

        assert graph_a.id == graph_b.id

        assert graph_a.content_id != graph_b.content_id

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

        graph_a = CompositeGraph(
            edges=frozenset({edge_a}),
            nodes=frozenset({node_x, node_y}),
            root_id=node_x.id,
        )
        graph_b = CompositeGraph(
            edges=frozenset({edge_b}),
            nodes=frozenset({node_x, node_y}),
            root_id=node_x.id,
        )

        assert graph_a.id == graph_b.id

        assert graph_a.content_id != graph_b.content_id


class TestGraphMerge:
    def test_unions_nodes_and_edges_from_both_graphs(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        root = make_fake_node()
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge_a = make_fake_edge(source_id=root.id, target_id=node_a.id)
        edge_b = make_fake_edge(source_id=root.id, target_id=node_b.id)

        graph_a = CompositeGraph(
            edges=frozenset({edge_a}),
            nodes=frozenset({root, node_a}),
            root_id=root.id,
        )
        graph_b = CompositeGraph(
            edges=frozenset({edge_b}),
            nodes=frozenset({root, node_b}),
            root_id=root.id,
        )

        merged = graph_a.merge(other=graph_b)

        assert merged.nodes == frozenset({root, node_a, node_b})
        assert merged.edges == frozenset({edge_a, edge_b})

    def test_keeps_the_root_id_of_the_graph_merge_is_called_on(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        root = make_fake_node()
        other_node = make_fake_node()

        graph_a = CompositeGraph(
            edges=frozenset(), nodes=frozenset({root}), root_id=root.id
        )
        graph_b = CompositeGraph(
            edges=frozenset(), nodes=frozenset({root, other_node}), root_id=root.id
        )

        merged = graph_a.merge(other=graph_b)

        assert merged.root_id == root.id

    def test_deduplicates_shared_nodes_and_edges(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        root = make_fake_node()
        node = make_fake_node()
        edge = make_fake_edge(source_id=root.id, target_id=node.id)

        graph_a = CompositeGraph(
            edges=frozenset({edge}), nodes=frozenset({root, node}), root_id=root.id
        )
        graph_b = CompositeGraph(
            edges=frozenset({edge}), nodes=frozenset({root, node}), root_id=root.id
        )

        merged = graph_a.merge(other=graph_b)

        assert merged.nodes == frozenset({root, node})
        assert merged.edges == frozenset({edge})

    def test_holds_one_version_of_a_node_present_in_both_graphs(self) -> None:
        version_a = FakeNodeWithContentIdentity(content="root", extra_field="value_a")
        version_b = FakeNodeWithContentIdentity(content="root", extra_field="value_b")

        assert version_a.id == version_b.id

        assert version_a.content_id != version_b.content_id

        graph_a = CompositeGraph(
            edges=frozenset(), nodes=frozenset({version_a}), root_id=version_a.id
        )
        graph_b = CompositeGraph(
            edges=frozenset(), nodes=frozenset({version_b}), root_id=version_a.id
        )

        merged = graph_a.merge(other=graph_b)

        assert len(merged.nodes) == 1

        assert next(iter(merged.nodes)) in {version_a, version_b}

    def test_keeps_the_receivers_version_of_a_node_present_in_both_graphs(self) -> None:
        version_a = FakeNodeWithContentIdentity(content="root", extra_field="value_a")
        version_b = FakeNodeWithContentIdentity(content="root", extra_field="value_b")
        graph_a = CompositeGraph(
            edges=frozenset(), nodes=frozenset({version_a}), root_id=version_a.id
        )
        graph_b = CompositeGraph(
            edges=frozenset(), nodes=frozenset({version_b}), root_id=version_a.id
        )

        assert next(iter(graph_a.merge(other=graph_b).nodes)).content_id == (
            version_a.content_id
        )

        assert next(iter(graph_b.merge(other=graph_a).nodes)).content_id == (
            version_b.content_id
        )

    def test_keeps_the_receivers_version_of_an_edge_present_in_both_graphs(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        source = make_fake_node()
        target = make_fake_node()
        version_a = FakeVersionedEdge(
            source_id=source.id, target_id=target.id, content="link", label="a"
        )
        version_b = FakeVersionedEdge(
            source_id=source.id, target_id=target.id, content="link", label="b"
        )

        assert version_a.id == version_b.id

        assert version_a.content_id != version_b.content_id

        nodes = frozenset({source, target})
        graph_a = CompositeGraph(
            edges=frozenset({version_a}), nodes=nodes, root_id=source.id
        )
        graph_b = CompositeGraph(
            edges=frozenset({version_b}), nodes=nodes, root_id=source.id
        )

        assert next(iter(graph_a.merge(other=graph_b).edges)).content_id == (
            version_a.content_id
        )

        assert next(iter(graph_b.merge(other=graph_a).edges)).content_id == (
            version_b.content_id
        )

    def test_keeps_the_graph_id_when_the_other_graph_holds_a_newer_node_version(
        self,
    ) -> None:
        version_a = FakeNodeWithContentIdentity(content="root", extra_field="value_a")
        version_b = FakeNodeWithContentIdentity(content="root", extra_field="value_b")
        graph_a = CompositeGraph(
            edges=frozenset(), nodes=frozenset({version_a}), root_id=version_a.id
        )
        graph_b = CompositeGraph(
            edges=frozenset(), nodes=frozenset({version_b}), root_id=version_a.id
        )

        merged = graph_a.merge(other=graph_b)

        assert merged.id == graph_a.id

        assert merged.id == graph_b.id

    def test_graph_id_is_the_same_whichever_graph_merge_is_called_on(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        root = make_fake_node()
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge_a = make_fake_edge(source_id=root.id, target_id=node_a.id)
        edge_b = make_fake_edge(source_id=root.id, target_id=node_b.id)
        graph_a = CompositeGraph(
            edges=frozenset({edge_a}),
            nodes=frozenset({root, node_a}),
            root_id=root.id,
        )
        graph_b = CompositeGraph(
            edges=frozenset({edge_b}),
            nodes=frozenset({root, node_b}),
            root_id=root.id,
        )

        assert graph_a.merge(other=graph_b).id == graph_b.merge(other=graph_a).id

    def test_merging_the_same_graph_again_changes_nothing(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        root = make_fake_node()
        node = make_fake_node()
        edge = make_fake_edge(source_id=root.id, target_id=node.id)
        graph_a = CompositeGraph(
            edges=frozenset({edge}), nodes=frozenset({root, node}), root_id=root.id
        )
        graph_b = CompositeGraph(
            edges=frozenset(), nodes=frozenset({root}), root_id=root.id
        )

        merged = graph_a.merge(other=graph_b)
        merged_again = merged.merge(other=graph_b)

        assert merged_again.id == merged.id

        assert merged_again.content_id == merged.content_id

        assert merged_again.nodes == merged.nodes

        assert merged_again.edges == merged.edges

    def test_does_not_mutate_either_input_graph(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        root = make_fake_node()
        node = make_fake_node()
        edge = make_fake_edge(source_id=root.id, target_id=node.id)
        graph_a = CompositeGraph(
            edges=frozenset(), nodes=frozenset({root}), root_id=root.id
        )
        graph_b = CompositeGraph(
            edges=frozenset({edge}), nodes=frozenset({root, node}), root_id=root.id
        )

        graph_a.merge(other=graph_b)

        assert graph_a.nodes == frozenset({root})

        assert graph_a.edges == frozenset()

        assert graph_b.nodes == frozenset({root, node})

        assert graph_b.edges == frozenset({edge})


class TestGraphValidation:
    def test_raises_with_empty_node_set(self, make_fake_node: MakeFakeNode) -> None:
        node = make_fake_node()

        with pytest.raises(GraphHasNoNodesError):
            CompositeGraph(edges=frozenset(), nodes=frozenset(), root_id=node.id)

    def test_raises_when_root_is_absent_from_nodes(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()
        root_id = uuid4()

        with pytest.raises(GraphRootNotInNodesError) as exception:
            CompositeGraph(edges=frozenset(), nodes=frozenset({node}), root_id=root_id)

        assert str(root_id) in str(exception.value)

    def test_raises_when_edge_references_unknown_node(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()
        nonexistent_id = uuid4()
        edge = make_fake_edge(source_id=nonexistent_id, target_id=node.id)

        with pytest.raises(GraphInconsistentError):
            CompositeGraph(
                edges=frozenset({edge}), nodes=frozenset({node}), root_id=node.id
            )

    def test_raises_when_an_edge_inverse_does_not_invert_back(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        source = make_fake_node()
        target = make_fake_node()
        edge = FakeOneWayEdge(source_id=source.id, target_id=target.id, content="x")

        with pytest.raises(GraphBrokenInversionError) as exception:
            CompositeGraph(
                edges=frozenset({edge}),
                nodes=frozenset({source, target}),
                root_id=source.id,
            )

        assert str(edge.id) in str(exception.value)


class TestGraphValidationOrder:
    def test_reports_an_unknown_endpoint_before_the_empty_node_set(
        self, make_fake_edge: MakeFakeEdge
    ) -> None:
        with pytest.raises(GraphInconsistentError):
            CompositeGraph(
                edges=frozenset({make_fake_edge()}),
                nodes=frozenset(),
                root_id=uuid4(),
            )

    def test_reports_an_unknown_endpoint_before_the_absent_root(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()

        with pytest.raises(GraphInconsistentError):
            CompositeGraph(
                edges=frozenset({make_fake_edge(source_id=uuid4(), target_id=node.id)}),
                nodes=frozenset({node}),
                root_id=uuid4(),
            )

    def test_reports_a_broken_inversion_before_an_unknown_endpoint(
        self,
    ) -> None:
        edge = FakeOneWayEdge(source_id=uuid4(), target_id=uuid4(), content="x")

        with pytest.raises(GraphBrokenInversionError):
            CompositeGraph(edges=frozenset({edge}), nodes=frozenset(), root_id=uuid4())

    def test_reports_the_empty_node_set_before_the_absent_root(self) -> None:
        with pytest.raises(GraphHasNoNodesError):
            CompositeGraph(edges=frozenset(), nodes=frozenset(), root_id=uuid4())


class TestGraphFlatten:
    def test_flattened_graph_keeps_the_id_and_the_content_id(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        source = make_fake_node()
        target = make_fake_node()
        edge = make_fake_edge(source_id=source.id, target_id=target.id)
        graph = CompositeGraph(
            edges=frozenset({edge}),
            nodes=frozenset({source, target}),
            root_id=source.id,
        )

        flattened = graph.flatten()

        assert flattened.id == graph.id

        assert flattened.content_id == graph.content_id

    def test_flattened_graph_holds_one_ref_per_node_and_edge(
        self, make_fake_edge: MakeFakeEdge, make_fake_node: MakeFakeNode
    ) -> None:
        source = make_fake_node()
        target = make_fake_node()
        edge = make_fake_edge(source_id=source.id, target_id=target.id)
        graph = CompositeGraph(
            edges=frozenset({edge}),
            nodes=frozenset({source, target}),
            root_id=source.id,
        )

        flattened = graph.flatten()

        assert flattened.nodes == frozenset({source.ref, target.ref})

        assert flattened.edges == frozenset(edge.ref for edge in graph.edges)

        assert flattened.root_id == graph.root_id

    def test_flattened_graph_rejects_two_refs_to_the_same_entity(
        self, make_fake_node: MakeFakeNode
    ) -> None:
        node = make_fake_node()
        stale = EntityRef(entity_type=type(node), id=node.id, content_id=uuid4())

        with pytest.raises(GraphDuplicateEntityError) as exception:
            FlattenedGraph(
                edges=frozenset(),
                nodes=frozenset({node.ref, stale}),
                root_id=node.id,
            )

        assert str(node.id) in str(exception.value)
