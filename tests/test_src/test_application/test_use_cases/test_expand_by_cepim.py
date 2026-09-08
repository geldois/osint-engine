from __future__ import annotations

from typing import TYPE_CHECKING, override

import pytest

from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.use_cases.expansion.expand_by_cepim import ExpandByCEPIM
from osint_engine.domain.entities.nodes.company import Company
from tests.fakes.fetchers import FakeCEPIMFetcher

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph
    from tests.conftest import (
        MakeEntityRecord,
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

_CNPJ = "10000000000000"


def _make_stub() -> Company:
    return Company(
        activity_start_date=None,
        cnpj=_CNPJ,
        is_headquarters=None,
        legal_name=None,
        legal_nature=None,
        registration_status=None,
        registration_status_date=None,
        registration_status_reason=None,
        share_capital=None,
        size_category=None,
        trade_name=None,
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


class _CountingCEPIMFetcher(FakeCEPIMFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        super().__init__(revision=revision)
        self.call_count = 0

    @override
    async def fetch(
        self, *, cnpj: str, cepim_id: int | None, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self.call_count += 1

        return await super().fetch(cnpj=cnpj, cepim_id=cepim_id, credential=credential)


class TestExpandByCEPIMReuseLock:
    @pytest.mark.asyncio
    async def test_raises_already_fetched_without_calling_the_fetcher_again(
        self,
        make_entity_record: MakeEntityRecord,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        previous = make_entity_record(entity_id=_make_stub().id, provider="cepim")
        mem_storage = make_mem_storage(
            external_credentials=[credential], entity_records=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = _CountingCEPIMFetcher(revision=None)

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cepim_fetcher=cepim_fetcher,
            cnpj=_CNPJ,
            cepim_id=None,
            username="alice",
        )

        with pytest.raises(AlreadyFetchedError) as exception:
            await use_case.execute()

        assert exception.value.entity_id == _make_stub().id
        assert exception.value.provider == "cepim"
        assert cepim_fetcher.call_count == 0

    @pytest.mark.asyncio
    async def test_force_true_bypasses_the_lock_and_calls_the_fetcher(
        self,
        make_entity_record: MakeEntityRecord,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        previous = make_entity_record(entity_id=_make_stub().id, provider="cepim")
        mem_storage = make_mem_storage(
            external_credentials=[credential], entity_records=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = _CountingCEPIMFetcher(
            revision=make_entity_revision(entity=make_graph())
        )

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cepim_fetcher=cepim_fetcher,
            cnpj=_CNPJ,
            cepim_id=None,
            force=True,
            username="alice",
        )

        result = await use_case.execute()

        assert result is not None
        assert cepim_fetcher.call_count == 1

    @pytest.mark.asyncio
    async def test_a_revision_from_a_different_provider_does_not_trigger_the_lock(
        self,
        make_entity_record: MakeEntityRecord,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        previous = make_entity_record(entity_id=_make_stub().id, provider="brasilapi")
        mem_storage = make_mem_storage(
            external_credentials=[credential], entity_records=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = _CountingCEPIMFetcher(
            revision=make_entity_revision(entity=make_graph())
        )

        use_case = ExpandByCEPIM(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cepim_fetcher=cepim_fetcher,
            cnpj=_CNPJ,
            cepim_id=None,
            username="alice",
        )

        result = await use_case.execute()

        assert result is not None
        assert cepim_fetcher.call_count == 1

    @pytest.mark.asyncio
    async def test_already_fetched_records_the_blocked_attempt(
        self,
        make_entity_record: MakeEntityRecord,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(username="alice")
        previous = make_entity_record(entity_id=_make_stub().id, provider="cepim")
        mem_storage = make_mem_storage(
            external_credentials=[credential], entity_records=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cepim_fetcher = _CountingCEPIMFetcher(revision=None)

        with pytest.raises(AlreadyFetchedError):
            await ExpandByCEPIM(
                uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
                cepim_fetcher=cepim_fetcher,
                cnpj=_CNPJ,
                cepim_id=None,
                username="alice",
            ).execute()

        record = next(
            r for r in mem_storage.entity_records if r.outcome == "already_fetched"
        )

        assert record.entity_id == _make_stub().id
        assert record.entity_ref == previous.entity_ref
        assert record.username == "alice"
