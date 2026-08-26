from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.use_cases.expansion.expand_by_cepim import ExpandByCEPIM
from tests.fakes.fetchers import FakeCEPIMFetcher

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeExternalCredential,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import (
        MakeFakeCEPIMFetcher,
        MakeMemUoWFactory,
    )


class TestExpandByCEPIMOrchestration:
    @pytest.mark.asyncio
    async def test_returns_the_revision_the_repository_stored(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_cepim_fetcher: MakeFakeCEPIMFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        credential = make_external_credential(username="alice")
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = make_fake_cepim_fetcher(revision=revision)

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cepim_fetcher=cepim_fetcher,
            cnpj="10000000000000",
            cepim_id=None,
            username="alice",
        )

        result = await use_case.execute()

        assert result is not None
        assert result.entity is revision.entity

    @pytest.mark.asyncio
    async def test_persists_the_fetched_revision_to_storage(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_cepim_fetcher: MakeFakeCEPIMFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=make_graph())
        credential = make_external_credential(username="alice")
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = make_fake_cepim_fetcher(revision=revision)

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cepim_fetcher=cepim_fetcher,
            cnpj="10000000000000",
            cepim_id=None,
            username="alice",
        )

        await use_case.execute()

        graph = revision.entity

        assert mem_storage.graphs[graph.id][graph.content_id] is revision

    @pytest.mark.asyncio
    async def test_raises_when_credential_is_missing(
        self,
        make_fake_cepim_fetcher: MakeFakeCEPIMFetcher,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        cepim_fetcher = make_fake_cepim_fetcher()

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(),
            cepim_fetcher=cepim_fetcher,
            cnpj="10000000000000",
            cepim_id=None,
            username="unknown_user",
        )

        with pytest.raises(ExternalCredentialNotFoundError) as exception:
            await use_case.execute()

        assert exception.value.username == "unknown_user"

    @pytest.mark.asyncio
    async def test_returns_none_and_skips_persistence_when_no_sanctions_are_found(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = FakeCEPIMFetcher(revision=None)

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cepim_fetcher=cepim_fetcher,
            cnpj="10000000000000",
            cepim_id=None,
            username="alice",
        )

        result = await use_case.execute()

        assert result is None
        assert not mem_storage.graphs
