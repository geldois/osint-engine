from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.infrastructure.persistence.mem.mem_storage import (
    MemStorage,
    MemStorageSnapshot,
)

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeEdge,
        MakeFakeNode,
        MakeGraph,
        MakeMemStorage,
        MakeUser,
    )


def _seeded_storage(
    *,
    make_entity_revision: MakeEntityRevision,
    make_fake_edge: MakeFakeEdge,
    make_graph: MakeGraph,
    make_fake_node: MakeFakeNode,
    make_user: MakeUser,
    make_mem_storage: MakeMemStorage,
) -> MemStorage:
    node_a = make_fake_node()
    node_b = make_fake_node()
    edge = make_fake_edge(source_id=node_a.id, target_id=node_b.id)
    graph = make_graph(edges=[edge], nodes=[node_a, node_b], root_id=node_a.id)

    return make_mem_storage(
        edges=[make_entity_revision(entity=edge)],
        graphs=[make_entity_revision(entity=graph)],
        nodes=[
            make_entity_revision(entity=node_a),
            make_entity_revision(entity=node_b),
        ],
        users=[make_user()],
    )


class TestMemStorageSnapshotSubclassContract:
    def test_inherits_directly_from_mem_storage(self) -> None:
        assert MemStorage in MemStorageSnapshot.__bases__


class TestMemStorageSnapshotSnapshot:
    def test_isolates_containers_while_sharing_leaf_revisions(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
    ) -> None:
        mem_storage = _seeded_storage(
            make_entity_revision=make_entity_revision,
            make_fake_edge=make_fake_edge,
            make_graph=make_graph,
            make_fake_node=make_fake_node,
            make_user=make_user,
            make_mem_storage=make_mem_storage,
        )

        snapshot = MemStorageSnapshot(mem_storage=mem_storage)

        assert mem_storage.edges is not snapshot.edges

        assert mem_storage.graphs is not snapshot.graphs

        assert mem_storage.nodes is not snapshot.nodes

        assert mem_storage.users is not snapshot.users

        (node_id, revisions), *_ = mem_storage.nodes.items()
        (content_id, revision), *_ = revisions.items()

        assert snapshot.nodes[node_id][content_id] is revision

    def test_clear_empties_every_inner_storage(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
    ) -> None:
        snapshot = MemStorageSnapshot(
            mem_storage=_seeded_storage(
                make_entity_revision=make_entity_revision,
                make_fake_edge=make_fake_edge,
                make_graph=make_graph,
                make_fake_node=make_fake_node,
                make_user=make_user,
                make_mem_storage=make_mem_storage,
            )
        )

        snapshot.clear_snapshot()

        assert not snapshot.edges

        assert not snapshot.graphs

        assert not snapshot.nodes

        assert not snapshot.users


class TestMemStorageSnapshotCommit:
    def test_commit_merges_a_new_entry_written_on_the_snapshot_into_the_backing_storage(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
    ) -> None:
        mem_storage = _seeded_storage(
            make_entity_revision=make_entity_revision,
            make_fake_edge=make_fake_edge,
            make_graph=make_graph,
            make_fake_node=make_fake_node,
            make_user=make_user,
            make_mem_storage=make_mem_storage,
        )
        snapshot = MemStorageSnapshot(mem_storage=mem_storage)

        new_node = make_fake_node()
        new_revision = make_entity_revision(entity=new_node)
        snapshot.nodes[new_node.id][new_node.content_id] = new_revision

        snapshot.commit_to_storage()

        assert mem_storage.nodes[new_node.id][new_node.content_id] == new_revision

    def test_commit_does_not_erase_an_entry_a_concurrent_transaction_committed_first(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_graph: MakeGraph,
        make_fake_node: MakeFakeNode,
        make_user: MakeUser,
        make_mem_storage: MakeMemStorage,
    ) -> None:
        mem_storage = _seeded_storage(
            make_entity_revision=make_entity_revision,
            make_fake_edge=make_fake_edge,
            make_graph=make_graph,
            make_fake_node=make_fake_node,
            make_user=make_user,
            make_mem_storage=make_mem_storage,
        )

        early_snapshot = MemStorageSnapshot(mem_storage=mem_storage)
        late_snapshot = MemStorageSnapshot(mem_storage=mem_storage)

        new_node = make_fake_node()
        new_graph = make_graph(edges=[], nodes=[new_node], root_id=new_node.id)
        new_graph_revision = make_entity_revision(entity=new_graph)
        early_snapshot.graphs[new_graph.id][new_graph.content_id] = new_graph_revision
        early_snapshot.commit_to_storage()

        assert new_graph.id in mem_storage.graphs

        late_snapshot.commit_to_storage()

        assert (
            mem_storage.graphs[new_graph.id][new_graph.content_id] == new_graph_revision
        )
