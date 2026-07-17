from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.domain.errors.entity_error import EntityNotFoundError

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRevision, MakeGraph, MakeMemStorage
    from tests.test_infrastructure.test_persistence.test_mem.test_mem_repositories.conftest import (  # noqa: E501
        MakeMemGraphRepository,
    )


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


# TESTS


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
