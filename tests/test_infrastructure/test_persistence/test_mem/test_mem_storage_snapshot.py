from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.infrastructure.persistence.mem.mem_storage import (
    MemStorage,
    MemStorageSnapshot,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEdge, MakeGraph, MakeNode

# VALID CASES


def test_mem_storage_snapshot_inherits_directly_from_mem_storage() -> None:
    bases = MemStorageSnapshot.__bases__

    assert MemStorage in bases


def test_mem_storage_snapshot_copies_object_references_from_mem_storage(
    make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
) -> None:
    edge = make_edge()
    node = make_node()
    graph = make_graph(edges=[edge], nodes=[node], root_id=node.id)
    mem_storage = MemStorage(
        edges={edge.id: edge}, graphs={graph.id: graph}, nodes={node.id: node}
    )

    snapshot = MemStorageSnapshot(mem_storage=mem_storage)

    assert mem_storage.edges is not snapshot.edges

    assert mem_storage.graphs is not snapshot.graphs

    assert mem_storage.nodes is not snapshot.nodes

    assert mem_storage.edges[edge.id] is snapshot.edges[edge.id]

    assert mem_storage.graphs[graph.id] is snapshot.graphs[graph.id]

    assert mem_storage.nodes[node.id] is snapshot.nodes[node.id]


def test_mem_storage_snapshot_cleans_all_object_references_in_its_inner_storages(
    make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
) -> None:
    edge = make_edge()
    node = make_node()
    graph = make_graph(edges=[edge], nodes=[node], root_id=node.id)
    mem_storage = MemStorage(
        edges={edge.id: edge}, graphs={graph.id: graph}, nodes={node.id: node}
    )
    snapshot = MemStorageSnapshot(mem_storage=mem_storage)

    snapshot.clear_snapshot()

    assert not (snapshot.edges and snapshot.edges is None)

    assert not (snapshot.graphs and snapshot.graphs is None)

    assert not (snapshot.nodes and snapshot.nodes is None)


def test_mem_storage_snapshot_only_commits_diff_to_mem_storage_explicitly(
    make_edge: MakeEdge, make_graph: MakeGraph, make_node: MakeNode
) -> None:
    edge = make_edge()
    node = make_node()
    graph = make_graph(edges=[edge], nodes=[node], root_id=node.id)
    mem_storage = MemStorage(
        edges={edge.id: edge}, graphs={graph.id: graph}, nodes={node.id: node}
    )
    snapshot = MemStorageSnapshot(mem_storage=mem_storage)

    snapshot.clear_snapshot()

    assert (edge.id, edge) in mem_storage.edges.items()

    assert (graph.id, graph) in mem_storage.graphs.items()

    assert (node.id, node) in mem_storage.nodes.items()

    snapshot.commit_to_storage()

    assert mem_storage.edges == snapshot.edges

    assert mem_storage.graphs == snapshot.graphs

    assert mem_storage.nodes == snapshot.nodes
