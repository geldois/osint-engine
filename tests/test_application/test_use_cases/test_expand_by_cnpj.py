from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ

if TYPE_CHECKING:
    from tests.conftest import (
        MakeFakeCNPJFetcher,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
        MakeMemUoWFactory,
    )


class TestExpandByCNPJOrchestration:
    @pytest.mark.asyncio
    async def test_returns_graph_produced_by_fetcher(
        self,
        make_fake_cnpj_fetcher: MakeFakeCNPJFetcher,
        make_graph: MakeGraph,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_uow_factory = make_mem_uow_factory()
        graph = make_graph()
        cnpj_fetcher = make_fake_cnpj_fetcher(graph=graph)

        use_case = ExpandByCNPJ(
            uow_factory=mem_uow_factory,
            cnpj_fetcher=cnpj_fetcher,
            cnpj="10000000000000",
        )

        result = await use_case.execute()

        assert result is graph

    @pytest.mark.asyncio
    async def test_persists_graph_to_storage_after_execute(
        self,
        make_fake_cnpj_fetcher: MakeFakeCNPJFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        mem_uow_factory = make_mem_uow_factory(mem_uow=mem_uow)
        graph = make_graph()
        cnpj_fetcher = make_fake_cnpj_fetcher(graph=graph)

        use_case = ExpandByCNPJ(
            uow_factory=mem_uow_factory,
            cnpj_fetcher=cnpj_fetcher,
            cnpj="10000000000000",
        )

        await use_case.execute()

        assert graph.id in mem_storage.graphs
