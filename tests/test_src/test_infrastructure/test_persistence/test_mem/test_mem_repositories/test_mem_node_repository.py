from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.application.revision.policies.revision_merge_policy import (
    merge_by_filled_fields_policy,
)
from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)
from osint_engine.domain.errors.entity_error import EntityNotFoundError
from tests.fakes.domain import FakeMergeableNode

if TYPE_CHECKING:
    from tests.fixtures.application import MakeEntityRevision, MakePolicies
    from tests.fixtures.domain import MakeFakeMergeableNode, MakeFakeNode
    from tests.fixtures.persistence import MakeMemNodeRepository, MakeMemStorage


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


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


class TestMemNodeRepositoryListByType:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_when_no_node_of_the_type_is_stored(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        assert await repo.list_by_type(node_type=FakeMergeableNode) == ()

    @pytest.mark.asyncio
    async def test_returns_only_revisions_whose_entity_matches_the_type(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        fake_revision = make_entity_revision(entity=make_fake_node())
        mergeable_revision = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="a")
        )
        repo = make_mem_node_repository(
            mem_storage=make_mem_storage(nodes=[fake_revision, mergeable_revision])
        )

        found = await repo.list_by_type(node_type=FakeMergeableNode)

        assert found == (mergeable_revision,)

    @pytest.mark.asyncio
    async def test_returns_the_selection_policy_pick_for_each_node_id(
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

        found = await repo.list_by_type(node_type=FakeMergeableNode)

        assert found == (newer,)


class TestMemNodeRepositoryListRevisions:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unseen_id(
        self,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        repo = make_mem_node_repository(mem_storage=make_mem_storage())

        assert await repo.list_revisions(id_=make_fake_node().id) == ()

    @pytest.mark.asyncio
    async def test_returns_every_revision_merged_for_the_same_id(
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
        repo = make_mem_node_repository(mem_storage=make_mem_storage())

        await repo.merge(revision=older)
        await repo.merge(revision=newer)

        found = await repo.list_revisions(id_=older.entity.id)

        assert {revision.entity.content_id for revision in found} == {
            older.entity.content_id,
            newer.entity.content_id,
        }


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
        make_policies: MakePolicies,
    ) -> None:
        stored = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="preserved"),
            fetched_at=_EARLY,
        )
        incoming = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label=None), fetched_at=_LATE
        )
        repo = make_mem_node_repository(
            mem_storage=make_mem_storage(nodes=[stored]),
            policies_override=make_policies(
                revision_merge_policy=merge_by_filled_fields_policy,
                revision_selection_policy=select_current_by_newest_fetched,
            ),
        )

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


class TestMemNodeRepositoryFindMany:
    @pytest.mark.asyncio
    async def test_returns_an_empty_tuple_for_no_pairs(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        repo = make_mem_node_repository(mem_storage=make_mem_storage())

        assert await repo.find_many(id_pairs=()) == ()

    @pytest.mark.asyncio
    async def test_returns_one_slot_per_pair_in_the_given_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        first = make_entity_revision(entity=make_fake_node())
        second = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(
            mem_storage=make_mem_storage(nodes=[first, second])
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
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

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
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="a")
        )
        assert revision.entity.id != revision.entity.content_id
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        found = await repo.find_many(
            id_pairs=((revision.entity.content_id, revision.entity.id),)
        )

        assert found == (None,)

    @pytest.mark.asyncio
    async def test_a_pair_with_a_content_id_selects_exactly_that_version(
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

        found = await repo.find_many(
            id_pairs=(
                (older.entity.id, older.entity.content_id),
                (older.entity.id, None),
            )
        )

        assert found[0] is older

        assert found[1] is newer


class TestMemNodeRepositoryGetMany:
    @pytest.mark.asyncio
    async def test_returns_an_empty_tuple_for_no_pairs(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        repo = make_mem_node_repository(mem_storage=make_mem_storage())

        assert await repo.get_many(id_pairs=()) == ()

    @pytest.mark.asyncio
    async def test_returns_one_revision_per_pair_in_the_given_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        first = make_entity_revision(entity=make_fake_node())
        second = make_entity_revision(entity=make_fake_node())
        repo = make_mem_node_repository(
            mem_storage=make_mem_storage(nodes=[first, second])
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
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(entity=make_fake_node())
        missing_id = uuid4()
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

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
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_node_repository: MakeMemNodeRepository,
    ) -> None:
        revision = make_entity_revision(
            entity=make_fake_mergeable_node(key="k", label="a")
        )
        assert revision.entity.id != revision.entity.content_id
        repo = make_mem_node_repository(mem_storage=make_mem_storage(nodes=[revision]))

        with pytest.raises(EntityNotFoundError):
            await repo.get_many(
                id_pairs=((revision.entity.content_id, revision.entity.id),)
            )
