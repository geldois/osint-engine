from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.application.use_cases.history.list_graph_history import (
    ListGraphHistory,
)

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeFakeNode,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


class TestListGraphHistoryOrchestration:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_for_an_unseen_root_id(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow = make_mem_uow(mem_storage=make_mem_storage())

        use_case = ListGraphHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), root_id=uuid4()
        )

        assert await use_case.execute() == ()

    @pytest.mark.asyncio
    async def test_orders_the_graphs_by_fetched_at_regardless_of_insertion_order(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        root_node = make_fake_node()
        early = make_entity_revision(
            entity=make_graph(
                edges=frozenset(),
                nodes={root_node, make_fake_node()},
                root_id=root_node.id,
            ),
            fetched_at=_EARLY,
        )
        late = make_entity_revision(
            entity=make_graph(
                edges=frozenset(),
                nodes={root_node, make_fake_node()},
                root_id=root_node.id,
            ),
            fetched_at=_LATE,
        )
        mem_storage = make_mem_storage(graphs=[late, early])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow), root_id=root_node.id
        )

        graphs = await use_case.execute()

        assert graphs == (early, late)

    @pytest.mark.asyncio
    async def test_excludes_graphs_from_a_different_root_id(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        matching = make_entity_revision(entity=make_graph())
        other = make_entity_revision(entity=make_graph())
        mem_storage = make_mem_storage(graphs=[matching, other])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphHistory(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            root_id=matching.entity.root_id,
        )

        graphs = await use_case.execute()

        assert graphs == (matching,)
