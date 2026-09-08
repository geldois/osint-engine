from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.history.list_graph_catalog import (
    GraphCatalogEntry,
    ListGraphCatalog,
)

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRecord,
        MakeEntityRevision,
        MakeFakeNode,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import MakeMemUoWFactory


_EARLY = datetime(2026, 1, 1, tzinfo=UTC)
_MID = datetime(2026, 3, 1, tzinfo=UTC)
_LATE = datetime(2026, 6, 1, tzinfo=UTC)


class TestListGraphCatalogOrchestration:
    @pytest.mark.asyncio
    async def test_returns_empty_tuple_when_nothing_was_ever_fetched(
        self,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow = make_mem_uow(mem_storage=make_mem_storage())

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        assert await use_case.execute() == ()

    @pytest.mark.asyncio
    async def test_a_single_revision_produces_a_single_entry_of_length_one(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=make_graph(), fetched_at=_EARLY)
        mem_storage = make_mem_storage(graphs=[revision])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        entries = await use_case.execute()

        assert entries == (
            GraphCatalogEntry(fetched_routes=frozenset(), revisions=(revision,)),
        )

    @pytest.mark.asyncio
    async def test_groups_revisions_sharing_a_root_even_with_distinct_graph_ids(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
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
        assert first.entity.id != second.entity.id

        mem_storage = make_mem_storage(graphs=[second, first])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        entries = await use_case.execute()

        assert entries == (
            GraphCatalogEntry(fetched_routes=frozenset(), revisions=(first, second)),
        )

    @pytest.mark.asyncio
    async def test_orders_entries_by_their_latest_revision_descending(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        stale_root = make_entity_revision(entity=make_graph(), fetched_at=_EARLY)
        fresh_root = make_entity_revision(entity=make_graph(), fetched_at=_LATE)
        mem_storage = make_mem_storage(graphs=[stale_root, fresh_root])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        entries = await use_case.execute()

        assert entries == (
            GraphCatalogEntry(fetched_routes=frozenset(), revisions=(fresh_root,)),
            GraphCatalogEntry(fetched_routes=frozenset(), revisions=(stale_root,)),
        )

    @pytest.mark.asyncio
    async def test_a_tie_between_two_roots_latest_revisions_does_not_raise(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        first_root = make_entity_revision(entity=make_graph(), fetched_at=_MID)
        second_root = make_entity_revision(entity=make_graph(), fetched_at=_MID)
        mem_storage = make_mem_storage(graphs=[first_root, second_root])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        entries = await use_case.execute()

        assert set(entries) == {
            GraphCatalogEntry(fetched_routes=frozenset(), revisions=(first_root,)),
            GraphCatalogEntry(fetched_routes=frozenset(), revisions=(second_root,)),
        }

    @pytest.mark.asyncio
    async def test_fetched_routes_collects_distinct_entity_record_providers(
        self,
        make_entity_record: MakeEntityRecord,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        root_node = make_fake_node()
        graph_revision = make_entity_revision(
            entity=make_graph(
                edges=frozenset(), nodes={root_node}, root_id=root_node.id
            ),
            fetched_at=_EARLY,
        )
        cnep_record = make_entity_record(entity_id=root_node.id, provider="cnep")
        pep_record = make_entity_record(entity_id=root_node.id, provider="pep")
        mem_storage = make_mem_storage(
            graphs=[graph_revision], entity_records=[cnep_record, pep_record]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        (entry,) = await use_case.execute()

        assert entry.fetched_routes == frozenset({"cnep", "pep"})

    @pytest.mark.asyncio
    async def test_fetched_routes_ignores_a_failed_or_invalid_entity_record(
        self,
        make_entity_record: MakeEntityRecord,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        root_node = make_fake_node()
        graph_revision = make_entity_revision(
            entity=make_graph(
                edges=frozenset(), nodes={root_node}, root_id=root_node.id
            ),
            fetched_at=_EARLY,
        )
        failed_record = make_entity_record(
            entity_id=root_node.id, outcome="failed", provider="cnep"
        )
        mem_storage = make_mem_storage(
            graphs=[graph_revision], entity_records=[failed_record]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        (entry,) = await use_case.execute()

        assert entry.fetched_routes == frozenset()

    @pytest.mark.asyncio
    async def test_fetched_routes_is_empty_when_no_entity_record_exists_for_the_root(
        self,
        make_entity_revision: MakeEntityRevision,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=make_graph(), fetched_at=_EARLY)
        mem_storage = make_mem_storage(graphs=[revision])
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        (entry,) = await use_case.execute()

        assert entry.fetched_routes == frozenset()


class TestListGraphCatalogIntegration:
    @pytest.mark.asyncio
    async def test_two_real_merges_of_a_growing_graph_produce_one_entry_of_count_two(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_node: MakeFakeNode,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        root_node = make_fake_node()
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)

        first = make_entity_revision(
            entity=make_graph(
                edges=frozenset(), nodes={root_node}, root_id=root_node.id
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

        async with mem_uow as uow:
            await uow.graphs.merge(revision=first)

        async with mem_uow as uow:
            await uow.graphs.merge(revision=second)

        assert first.entity.id != second.entity.id

        use_case = ListGraphCatalog(uow_factory=make_mem_uow_factory(mem_uow=mem_uow))

        entries = await use_case.execute()

        assert len(entries) == 1
        assert len(entries[0].revisions) == 2
