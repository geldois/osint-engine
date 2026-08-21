from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest

from osint_engine.application.revision.policies.revision_selection_policy import (
    select_current_by_newest_fetched,
)
from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.entity import Entity
    from tests.conftest import (
        MakeEntityRevision,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
        MakePolicies,
    )
    from tests.test_src.test_application.conftest import (
        MakeFakeCNPJFetcher,
        MakeMemUoWFactory,
    )


# TEST DOUBLES


def _keep_stored_policy[Entity_: Entity[UUID]](
    left: EntityRevision[Entity_], right: EntityRevision[Entity_], /
) -> EntityRevision[Entity_]:
    del right

    return left


# TESTS


class TestExpandByCNPJOrchestration:
    @pytest.mark.asyncio
    async def test_returns_the_revision_the_repository_stored(
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

        assert result is not None
        assert result.entity is revision.entity

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

    @pytest.mark.asyncio
    async def test_returns_what_the_merge_produced_not_what_the_fetcher_supplied(
        self,
        make_entity_revision: MakeEntityRevision,
        make_fake_cnpj_fetcher: MakeFakeCNPJFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
        make_policies: MakePolicies,
    ) -> None:
        graph = make_graph()
        stored = make_entity_revision(entity=graph, provider="already_stored")
        incoming = make_entity_revision(entity=graph, provider="just_fetched")

        mem_storage = make_mem_storage()
        mem_storage.graphs[graph.id][graph.content_id] = stored

        use_case = ExpandByCNPJ(
            uow_factory=make_mem_uow_factory(
                mem_uow=make_mem_uow(
                    mem_storage=mem_storage,
                    policies=make_policies(
                        revision_merge_policy=_keep_stored_policy,
                        revision_selection_policy=select_current_by_newest_fetched,
                    ),
                )
            ),
            cnpj_fetcher=make_fake_cnpj_fetcher(revision=incoming),
            cnpj="10000000000000",
        )

        result = await use_case.execute()

        assert result.provider == "already_stored"
        assert result is not incoming
