from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.infrastructure.persistence.mem.mem_storage import (
    MemStorage,
    MemStorageSnapshot,
)

if TYPE_CHECKING:
    from tests.conftest import MakeFakeEdge, MakeFakeNode, MakeGraph, MakeUser


class TestMemStorageSnapshotSubclassContract:
    def test_inherits_directly_from_mem_storage(self) -> None:
        bases = MemStorageSnapshot.__bases__

        assert MemStorage in bases


class TestMemStorageSnapshotSnapshot:
    def test_copies_object_references_from_mem_storage(
        self,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = MemStorage(
            edges={edge.id: edge},
            graphs={graph.id: graph},
            nodes={node_a.id: node_a, node_b.id: node_b},
            users={user.username: user},
        )

        snapshot = MemStorageSnapshot(mem_storage=mem_storage)

        assert mem_storage.edges is not snapshot.edges

        assert mem_storage.graphs is not snapshot.graphs

        assert mem_storage.nodes is not snapshot.nodes

        assert mem_storage.users is not snapshot.users

        assert mem_storage.edges[edge.id] is snapshot.edges[edge.id]

        assert mem_storage.graphs[graph.id] is snapshot.graphs[graph.id]

        assert mem_storage.nodes[node_a.id] is snapshot.nodes[node_a.id]

        assert mem_storage.nodes[node_b.id] is snapshot.nodes[node_b.id]

        assert mem_storage.users[user.username] is snapshot.users[user.username]

    def test_cleans_all_object_references_in_its_inner_storages(
        self,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = MemStorage(
            edges={edge.id: edge},
            graphs={graph.id: graph},
            nodes={node_a.id: node_a, node_b.id: node_b},
            users={user.username: user},
        )
        snapshot = MemStorageSnapshot(mem_storage=mem_storage)

        snapshot.clear_snapshot()

        assert not (snapshot.edges and snapshot.edges is None)

        assert not (snapshot.graphs and snapshot.graphs is None)

        assert not (snapshot.nodes and snapshot.nodes is None)

        assert not (snapshot.users and snapshot.users is None)


class TestMemStorageSnapshotCommit:
    def test_only_commits_diff_to_mem_storage_explicitly(
        self,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
    ) -> None:
        node_a = make_fake_node()
        node_b = make_fake_node()
        edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
        graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)
        user = make_user()
        mem_storage = MemStorage(
            edges={edge.id: edge},
            graphs={graph.id: graph},
            nodes={node_a.id: node_a, node_b.id: node_b},
            users={user.username: user},
        )
        snapshot = MemStorageSnapshot(mem_storage=mem_storage)

        snapshot.clear_snapshot()

        assert (edge.id, edge) in mem_storage.edges.items()

        assert (graph.id, graph) in mem_storage.graphs.items()

        assert (node_a.id, node_a) in mem_storage.nodes.items()

        assert (node_b.id, node_b) in mem_storage.nodes.items()

        assert (user.username, user) in mem_storage.users.items()

        snapshot.commit_to_storage()

        assert mem_storage.edges == snapshot.edges

        assert mem_storage.graphs == snapshot.graphs

        assert mem_storage.nodes == snapshot.nodes

        assert mem_storage.users == snapshot.users
