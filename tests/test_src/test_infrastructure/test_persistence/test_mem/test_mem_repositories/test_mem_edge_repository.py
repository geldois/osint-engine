from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.domain.errors.entity_error import EntityNotFoundError
from tests.fakes.domain import FakeDefaultEdge, FakeVersionedEdge

if TYPE_CHECKING:
    from tests.fixtures.application import MakeEntityRevision
    from tests.fixtures.domain import MakeFakeEdge
    from tests.fixtures.persistence import MakeMemEdgeRepository, MakeMemStorage


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


class TestMemEdgeRepositoryFind:
    @pytest.mark.asyncio
    async def test_returns_none_when_absent(
        self,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        repo = make_mem_edge_repository(mem_storage=make_mem_storage())

        assert await repo.find(id_=make_fake_edge().id) is None

    @pytest.mark.asyncio
    async def test_returns_the_stored_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        assert await repo.find(id_=revision.entity.id) is revision

    @pytest.mark.asyncio
    async def test_returns_the_exact_revision_by_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        found = await repo.find(
            id_=revision.entity.id, content_id=revision.entity.content_id
        )

        assert found is revision

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        assert await repo.find(id_=revision.entity.id, content_id=uuid4()) is None


class TestMemEdgeRepositoryGet:
    @pytest.mark.asyncio
    async def test_returns_the_stored_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        assert await repo.get(id_=revision.entity.id) is revision

    @pytest.mark.asyncio
    async def test_raises_with_id_and_subject_when_absent(
        self,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        edge = make_fake_edge()
        repo = make_mem_edge_repository(mem_storage=make_mem_storage())

        with pytest.raises(EntityNotFoundError) as exception:
            await repo.get(id_=edge.id)

        assert str(edge.id) in str(exception.value)

        assert "Edge" in str(exception.value)


class TestMemEdgeRepositoryListRevisions:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unseen_id(
        self,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        repo = make_mem_edge_repository(mem_storage=make_mem_storage())

        assert await repo.list_revisions(id_=make_fake_edge().id) == ()

    @pytest.mark.asyncio
    async def test_returns_every_revision_merged_for_the_same_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        source_id, target_id = uuid4(), uuid4()
        older = make_entity_revision(
            entity=FakeDefaultEdge(
                source_id=source_id, target_id=target_id, content="a"
            ),
            fetched_at=_EARLY,
        )
        newer = make_entity_revision(
            entity=FakeDefaultEdge(
                source_id=source_id, target_id=target_id, content="b"
            ),
            fetched_at=_LATE,
        )
        repo = make_mem_edge_repository(mem_storage=make_mem_storage())

        await repo.merge(revision=older)
        await repo.merge(revision=newer)

        found = await repo.list_revisions(id_=older.entity.id)

        assert {revision.entity.content_id for revision in found} == {
            older.entity.content_id,
            newer.entity.content_id,
        }


class TestMemEdgeRepositoryMerge:
    @pytest.mark.asyncio
    async def test_first_write_stores_the_revision_under_id_and_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        mem_storage = make_mem_storage()
        repo = make_mem_edge_repository(mem_storage=mem_storage)

        returned = await repo.merge(revision=revision)

        assert returned is revision

        assert (
            mem_storage.edges[revision.entity.id][revision.entity.content_id]
            is revision
        )

    @pytest.mark.asyncio
    async def test_with_an_existing_identical_edge_stores_the_newest_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        edge = make_fake_edge()
        stored = make_entity_revision(entity=edge, fetched_at=_EARLY)
        incoming = make_entity_revision(entity=edge, fetched_at=_LATE)
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[stored]))

        merged = await repo.merge(revision=incoming)

        assert merged is incoming

    @pytest.mark.asyncio
    async def test_many_persists_every_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        first = make_entity_revision(entity=make_fake_edge())
        second = make_entity_revision(entity=make_fake_edge())
        mem_storage = make_mem_storage()
        repo = make_mem_edge_repository(mem_storage=mem_storage)

        await repo.merge_many(revisions=frozenset({first, second}))

        assert first.entity.id in mem_storage.edges

        assert second.entity.id in mem_storage.edges


class TestMemEdgeRepositoryFindMany:
    @pytest.mark.asyncio
    async def test_returns_an_empty_tuple_for_no_pairs(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        repo = make_mem_edge_repository(mem_storage=make_mem_storage())

        assert await repo.find_many(id_pairs=()) == ()

    @pytest.mark.asyncio
    async def test_returns_one_slot_per_pair_in_the_given_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        first = make_entity_revision(entity=make_fake_edge())
        second = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(
            mem_storage=make_mem_storage(edges=[first, second])
        )

        found = await repo.find_many(
            id_pairs=(
                (second.entity.id, second.entity.content_id),
                (first.entity.id, first.entity.content_id),
            )
        )

        assert len(found) == 2

        assert found[0] is second

        assert found[1] is first

    @pytest.mark.asyncio
    async def test_leaves_none_in_the_slot_of_an_unknown_pair(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        found = await repo.find_many(
            id_pairs=(
                (revision.entity.id, revision.entity.content_id),
                (uuid4(), None),
            )
        )

        assert found[0] is revision

        assert found[1] is None

    @pytest.mark.asyncio
    async def test_reads_every_pair_as_id_then_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(
            entity=FakeVersionedEdge(
                source_id=uuid4(), target_id=uuid4(), content="link", label="a"
            )
        )
        assert revision.entity.id != revision.entity.content_id
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        found = await repo.find_many(
            id_pairs=((revision.entity.content_id, revision.entity.id),)
        )

        assert found == (None,)


class TestMemEdgeRepositoryGetMany:
    @pytest.mark.asyncio
    async def test_returns_an_empty_tuple_for_no_pairs(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        repo = make_mem_edge_repository(mem_storage=make_mem_storage())

        assert await repo.get_many(id_pairs=()) == ()

    @pytest.mark.asyncio
    async def test_returns_one_revision_per_pair_in_the_given_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        first = make_entity_revision(entity=make_fake_edge())
        second = make_entity_revision(entity=make_fake_edge())
        repo = make_mem_edge_repository(
            mem_storage=make_mem_storage(edges=[first, second])
        )

        found = await repo.get_many(
            id_pairs=(
                (second.entity.id, second.entity.content_id),
                (first.entity.id, first.entity.content_id),
            )
        )

        assert len(found) == 2

        assert found[0] is second

        assert found[1] is first

    @pytest.mark.asyncio
    async def test_raises_with_the_id_of_the_first_missing_pair(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_edge: MakeFakeEdge,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_edge())
        missing_id = uuid4()
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        with pytest.raises(EntityNotFoundError) as exception:
            await repo.get_many(
                id_pairs=(
                    (revision.entity.id, revision.entity.content_id),
                    (missing_id, None),
                )
            )

        assert str(missing_id) in str(exception.value)

    @pytest.mark.asyncio
    async def test_raises_when_a_pair_is_given_as_content_id_then_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_mem_storage: MakeMemStorage,
        make_mem_edge_repository: MakeMemEdgeRepository,
    ) -> None:
        revision = make_entity_revision(
            entity=FakeVersionedEdge(
                source_id=uuid4(), target_id=uuid4(), content="link", label="a"
            )
        )
        assert revision.entity.id != revision.entity.content_id
        repo = make_mem_edge_repository(mem_storage=make_mem_storage(edges=[revision]))

        with pytest.raises(EntityNotFoundError):
            await repo.get_many(
                id_pairs=((revision.entity.content_id, revision.entity.id),)
            )
