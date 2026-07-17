from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_application.conftest import (
        MakeFakeCNPJFetcher,
        MakeMemUoWFactory,
    )


class TestExpandByCNPJOrchestration:
    @pytest.mark.asyncio
    async def test_returns_the_graph_wrapped_by_the_fetched_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_cnpj_fetcher: MakeFakeCNPJFetcher,
        make_graph: MakeGraph,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        cnpj_fetcher = make_fake_cnpj_fetcher(revision=revision)

        use_case = ExpandByCNPJ(
            uow_factory=make_mem_uow_factory(),
            cnpj_fetcher=cnpj_fetcher,
            cnpj="10000000000000",
        )

        result = await use_case.execute()

        assert result is revision.entity

    @pytest.mark.asyncio
    async def test_persists_the_fetched_revision_to_storage(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_cnpj_fetcher: MakeFakeCNPJFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        mem_storage = make_mem_storage()
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cnpj_fetcher = make_fake_cnpj_fetcher(revision=revision)

        use_case = ExpandByCNPJ(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cnpj_fetcher=cnpj_fetcher,
            cnpj="10000000000000",
        )

        await use_case.execute()

        graph = revision.entity

        assert mem_storage.graphs[graph.id][graph.content_id] is revision
