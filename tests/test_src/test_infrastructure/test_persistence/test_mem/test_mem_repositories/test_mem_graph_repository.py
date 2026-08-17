from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.domain.errors.entity_error import EntityNotFoundError

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeNode,
        MakeGraph,
        MakeMemStorage,
    )
    from tests.test_src.test_infrastructure.test_persistence.test_mem.test_mem_repositories.conftest import (  # noqa: E501
        MakeMemGraphRepository,
    )


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


class TestMemGraphRepositoryFind:
    @pytest.mark.asyncio
    async def test_returns_none_when_absent(
        self,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        assert await repo.find(id_=make_graph().id) is None

    @pytest.mark.asyncio
    async def test_returns_the_stored_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        repo = make_mem_graph_repository(
            mem_storage=make_mem_storage(graphs=[revision])
        )

        assert await repo.find(id_=revision.entity.id) is revision

    @pytest.mark.asyncio
    async def test_returns_the_exact_revision_by_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        repo = make_mem_graph_repository(
            mem_storage=make_mem_storage(graphs=[revision])
        )

        found = await repo.find(
            id_=revision.entity.id, content_id=revision.entity.content_id
        )

        assert found is revision

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        repo = make_mem_graph_repository(
            mem_storage=make_mem_storage(graphs=[revision])
        )

        assert await repo.find(id_=revision.entity.id, content_id=uuid4()) is None


class TestMemGraphRepositoryGet:
    @pytest.mark.asyncio
    async def test_returns_the_stored_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        repo = make_mem_graph_repository(
            mem_storage=make_mem_storage(graphs=[revision])
        )

        assert await repo.get(id_=revision.entity.id) is revision

    @pytest.mark.asyncio
    async def test_raises_with_id_and_subject_when_absent(
        self,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        graph = make_graph()
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        with pytest.raises(EntityNotFoundError) as exception:
            await repo.get(id_=graph.id)

        assert str(graph.id) in str(exception.value)

        assert "Graph" in str(exception.value)


class TestMemGraphRepositoryListRevisions:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unseen_id(
        self,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        assert await repo.list_revisions(id_=make_graph().id) == ()

    @pytest.mark.asyncio
    async def test_returns_the_merged_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        await repo.merge(revision=revision)

        found = await repo.list_revisions(id_=revision.entity.id)

        assert found == (revision,)


class TestMemGraphRepositoryListRevisionsByRoot:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unseen_root_id(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        assert await repo.list_revisions_by_root(root_id=uuid4()) == ()

    @pytest.mark.asyncio
    async def test_returns_every_revision_sharing_the_root_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        root_node = make_fake_node()
        first = make_entity_revision(
            entity=make_graph(
                edges=frozenset(),
                nodes={root_node, make_fake_node()},
                root_id=root_node.id,
            ),
            fetched_at=_EARLY,
        )
        second = make_entity_revision(
            entity=make_graph(
                edges=frozenset(),
                nodes={root_node, make_fake_node()},
                root_id=root_node.id,
            ),
            fetched_at=_LATE,
        )
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        await repo.merge(revision=first)
        await repo.merge(revision=second)

        found = await repo.list_revisions_by_root(root_id=root_node.id)

        assert set(found) == {first, second}

    @pytest.mark.asyncio
    async def test_excludes_revisions_from_a_different_root_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        matching = make_entity_revision(entity=make_graph())
        other = make_entity_revision(entity=make_graph())
        repo = make_mem_graph_repository(mem_storage=make_mem_storage())

        await repo.merge(revision=matching)
        await repo.merge(revision=other)

        found = await repo.list_revisions_by_root(root_id=matching.entity.root_id)

        assert found == (matching,)


class TestMemGraphRepositoryMerge:
    @pytest.mark.asyncio
    async def test_first_write_stores_the_revision_under_id_and_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        mem_storage = make_mem_storage()
        repo = make_mem_graph_repository(mem_storage=mem_storage)

        returned = await repo.merge(revision=revision)

        assert returned is revision

        assert (
            mem_storage.graphs[revision.entity.id][revision.entity.content_id]
            is revision
        )

    @pytest.mark.asyncio
    async def test_with_an_existing_identical_graph_stores_the_newest_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        graph = make_graph()
        stored = make_entity_revision(entity=graph, fetched_at=_EARLY)
        incoming = make_entity_revision(entity=graph, fetched_at=_LATE)
        repo = make_mem_graph_repository(mem_storage=make_mem_storage(graphs=[stored]))

        merged = await repo.merge(revision=incoming)

        assert merged is incoming

    @pytest.mark.asyncio
    async def test_many_persists_every_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        first = make_entity_revision(entity=make_graph())
        second = make_entity_revision(entity=make_graph())
        mem_storage = make_mem_storage()
        repo = make_mem_graph_repository(mem_storage=mem_storage)

        await repo.merge_many(revisions=frozenset({first, second}))

        assert first.entity.id in mem_storage.graphs

        assert second.entity.id in mem_storage.graphs


class TestMemGraphRepositoryMergeCascade:
    @pytest.mark.asyncio
    async def test_every_node_becomes_individually_findable(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        graph = make_graph()
        revision = make_entity_revision(entity=graph)
        mem_storage = make_mem_storage()
        repo = make_mem_graph_repository(mem_storage=mem_storage)

        await repo.merge(revision=revision)

        for node in graph.nodes:
            assert node.id in mem_storage.nodes
            assert node.content_id in mem_storage.nodes[node.id]

    @pytest.mark.asyncio
    async def test_every_edge_becomes_individually_findable(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        graph = make_graph()
        revision = make_entity_revision(entity=graph)
        mem_storage = make_mem_storage()
        repo = make_mem_graph_repository(mem_storage=mem_storage)

        await repo.merge(revision=revision)

        for edge in graph.edges:
            assert edge.id in mem_storage.edges
            assert edge.content_id in mem_storage.edges[edge.id]

    @pytest.mark.asyncio
    async def test_cascaded_node_revision_carries_the_graph_revisions_provider(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:
        graph = make_graph()
        revision = make_entity_revision(entity=graph, provider="a_specific_source")
        mem_storage = make_mem_storage()
        repo = make_mem_graph_repository(mem_storage=mem_storage)

        await repo.merge(revision=revision)

        any_node = next(iter(graph.nodes))
        cascaded = mem_storage.nodes[any_node.id][any_node.content_id]

        assert cascaded.provider == "a_specific_source"

    @pytest.mark.asyncio
    async def test_re_merging_an_unchanged_graph_does_not_re_stamp_its_nodes(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_graph_repository: MakeMemGraphRepository,
    ) -> None:

        graph = make_graph()
        first = make_entity_revision(
            entity=graph, fetched_at=_EARLY, provider="original_source"
        )
        mem_storage = make_mem_storage()
        repo = make_mem_graph_repository(mem_storage=mem_storage)

        await repo.merge(revision=first)

        second = make_entity_revision(
            entity=graph, fetched_at=_LATE, provider="rediscovered_source"
        )

        await repo.merge(revision=second)

        any_node = next(iter(graph.nodes))
        cascaded = mem_storage.nodes[any_node.id][any_node.content_id]

        assert cascaded.fetched_at == _EARLY
        assert cascaded.provider == "original_source"
