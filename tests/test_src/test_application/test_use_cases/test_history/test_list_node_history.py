from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.application.use_cases.history.list_node_history import (
    ListNodeHistory,
)

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeMergeableNode,
        MakeFakeNode,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


class TestListNodeHistoryOrchestration:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unknown_node_id(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow = make_mem_uow(mem_storage=make_mem_storage())

        use_case = ListNodeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), node_id=uuid4()
        )

        assert await use_case.execute() == ()

    @pytest.mark.asyncio
    async def test_orders_two_observations_by_fetched_at_regardless_of_insertion_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        early = make_entity_revision(
            entity=make_fake_mergeable_node(key="10000000000", label="first seen"),
            fetched_at=_EARLY,
        )
        late = make_entity_revision(
            entity=make_fake_mergeable_node(key="10000000000", label="updated"),
            fetched_at=_LATE,
        )
        assert early.entity.id == late.entity.id
        assert early.entity.content_id != late.entity.content_id

        mem_storage = make_mem_storage(nodes=[late, early])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListNodeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), node_id=early.entity.id
        )

        history = await use_case.execute()

        assert history == (early, late)

    @pytest.mark.asyncio
    async def test_each_item_carries_its_own_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_mergeable_node: MakeFakeMergeableNode,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        early = make_entity_revision(
            entity=make_fake_mergeable_node(key="10000000000", label="first seen"),
            fetched_at=_EARLY,
        )
        late = make_entity_revision(
            entity=make_fake_mergeable_node(key="10000000000", label="updated"),
            fetched_at=_LATE,
        )
        mem_storage = make_mem_storage(nodes=[late, early])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListNodeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), node_id=early.entity.id
        )

        history = await use_case.execute()

        assert history[0].fetched_at != history[1].fetched_at

    @pytest.mark.asyncio
    async def test_excludes_observations_of_a_different_node(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        matching = make_entity_revision(entity=make_fake_node())
        other = make_entity_revision(entity=make_fake_node())
        mem_storage = make_mem_storage(nodes=[matching, other])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListNodeHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            node_id=matching.entity.id,
        )

        history = await use_case.execute()

        assert history == (matching,)
