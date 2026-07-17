from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.domain.errors.entity_error import EntityNotFoundError
from tests.fakes.domain import FakeMergeableNode

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeMergeableNode,
        MakeFakeNode,
        MakeMemStorage,
    )
    from tests.test_infrastructure.test_persistence.test_mem.test_mem_repositories.conftest import (  # noqa: E501
        MakeMemNodeRepository,
    )


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


# TESTS


class TestMemNodeRepositoryFind:
    @pytest.mark.asyncio
    async def test_returns_none_when_absent(
        self,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        repo = make_mem_node_repository(mem_storage=make_mem_storage())

        assert await repo.find(id_=make_fake_node().id) is None

    @pytest.mark.asyncio
    async def test_returns_the_stored_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        assert await repo.find(id_=revision.entity.id) is revision

    @pytest.mark.asyncio
    async def test_returns_the_selection_policy_pick_across_revisions(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        older = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="a"), fetched_at=_EARLY
        )
        newer = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="b"), fetched_at=_LATE
        )
        repo = make_mem_node_repository(
            mem_storage=make_mem_storage(nodes=[older, newer])
        )

        assert await repo.find(id_=older.entity.id) is newer

    @pytest.mark.asyncio
    async def test_returns_the_exact_revision_by_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        found = await repo.find(
            id_=revision.entity.id, content_id=revision.entity.content_id
        )

        assert found is revision

    @pytest.mark.asyncio
    async def test_returns_none_for_unknown_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        assert await repo.find(id_=revision.entity.id, content_id=uuid4()) is None


class TestMemNodeRepositoryGet:
    @pytest.mark.asyncio
    async def test_returns_the_stored_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        assert await repo.get(id_=revision.entity.id) is revision

    @pytest.mark.asyncio
    async def test_raises_with_id_and_subject_when_absent(
        self,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        node = make_fake_node()
        repo = make_mem_node_repository(mem_storage=make_mem_storage())

        with pytest.raises(EntityNotFoundError) as exception:
            await repo.get(id_=node.id)

        assert str(node.id) in str(exception.value)

        assert "Node" in str(exception.value)


class TestMemNodeRepositoryMerge:
    @pytest.mark.asyncio
    async def test_first_write_stores_the_revision_under_id_and_content_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        mem_storage = make_mem_storage()
        repo = make_mem_node_repository(mem_storage=mem_storage)

        returned = await repo.merge(revision=revision)

        assert returned is revision

        assert (
            mem_storage.nodes[revision.entity.id][revision.entity.content_id]
            is revision
        )

    @pytest.mark.asyncio
    async def test_reconciles_with_an_existing_revision_via_the_merge_policy(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        stored = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="preserved"),
            fetched_at=_EARLY,
        )
        incoming = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label=None), fetched_at=_LATE
        )
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[stored]))

        merged = await repo.merge(revision=incoming)

        entity = merged.entity
        assert isinstance(entity, FakeMergeableNode)

        assert entity.label == "preserved"

        assert merged.merged_at is not None

    @pytest.mark.asyncio
    async def test_many_persists_every_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        first = make_entity_revision(entity=make_fake_node())
        second = make_entity_revision(entity=make_fake_node())
        mem_storage = make_mem_storage()
        repo = make_mem_node_repository(mem_storage=mem_storage)

        await repo.merge_many(revisions=frozenset({first, second}))

        assert first.entity.id in mem_storage.nodes

        assert second.entity.id in mem_storage.nodes
