from __future__ import annotations

from typing import TYPE_CHECKING, override

import pytest

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person
from tests.fakes.fetchers import FakeCPFFetcher

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.revision.entity_revision import EntityRevision
    from tests.conftest import (
        MakeEntityRevision,
        MakeExternalCredential,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import (
        MakeFakeCPFFetcher,
        MakeMemUoWFactory,
    )

_CPF = "10000000000"


class _CountingCPFFetcher(FakeCPFFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        super().__init__(revision=revision)
        self.call_count = 0

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self.call_count += 1

        return await super().fetch(cpf=cpf, credential=credential)


def _make_stub(*, cpf: str = _CPF) -> Person:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=cpf,
        name=None,
        registration_date=None,
        registration_status=None,
    )


def _stub_id() -> object:
    return _make_stub().id


def _make_kipflow_graph() -> Graph:
    person = _make_stub()

    return Graph(edges=frozenset(), nodes=frozenset({person}), root_id=person.id)


class TestExpandByCPFOrchestration:
    @pytest.mark.asyncio
    async def test_returns_the_graph_wrapped_by_the_fetched_revision(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_cpf_fetcher: MakeFakeCPFFetcher,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=_make_kipflow_graph())
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = make_fake_cpf_fetcher(revision=revision)

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="alice",
        )

        result = await use_case.execute()

        assert result is revision.entity

    @pytest.mark.asyncio
    async def test_persists_the_fetched_revision_to_storage(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_cpf_fetcher: MakeFakeCPFFetcher,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        revision = make_entity_revision(entity=_make_kipflow_graph())
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = make_fake_cpf_fetcher(revision=revision)

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="alice",
        )

        await use_case.execute()

        graph = revision.entity

        assert mem_storage.graphs[graph.id][graph.content_id] is revision

    @pytest.mark.asyncio
    async def test_raises_when_credential_is_missing(
        self,
        make_fake_cpf_fetcher: MakeFakeCPFFetcher,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        cpf_fetcher = make_fake_cpf_fetcher()

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="unknown_user",
        )

        with pytest.raises(ExternalCredentialNotFoundError) as exception:
            await use_case.execute()

        assert exception.value.username == "unknown_user"

    @pytest.mark.asyncio
    async def test_returns_none_when_the_fetcher_finds_nothing(
        self,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = FakeCPFFetcher(revision=None)

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="alice",
        )

        result = await use_case.execute()

        assert result is None


class TestExpandByCPFReuseLock:
    @pytest.mark.asyncio
    async def test_raises_already_fetched_without_calling_the_fetcher_again(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        previous = make_entity_revision(entity=_make_stub(), provider="kipflow")
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = _CountingCPFFetcher(
            revision=make_entity_revision(entity=make_graph())
        )

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="alice",
        )

        with pytest.raises(AlreadyFetchedError) as exception:
            await use_case.execute()

        assert exception.value.entity_id == _stub_id()
        assert exception.value.provider == "kipflow"
        assert cpf_fetcher.call_count == 0

    @pytest.mark.asyncio
    async def test_force_true_bypasses_the_lock_and_calls_the_fetcher(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        previous = make_entity_revision(entity=_make_stub(), provider="kipflow")
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = _CountingCPFFetcher(
            revision=make_entity_revision(entity=_make_kipflow_graph())
        )

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            force=True,
            username="alice",
        )

        result = await use_case.execute()

        assert result is not None
        assert cpf_fetcher.call_count == 1

    @pytest.mark.asyncio
    async def test_a_revision_from_a_different_provider_does_not_trigger_the_lock(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        previous = make_entity_revision(entity=_make_stub(), provider="text_pattern")
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = _CountingCPFFetcher(
            revision=make_entity_revision(entity=_make_kipflow_graph())
        )

        use_case = ExpandByCPF(
            uow_factory=make_mem_uow_factory(mem_uow=mem_uow),
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="alice",
        )

        result = await use_case.execute()

        assert result is not None
        assert cpf_fetcher.call_count == 1

    @pytest.mark.asyncio
    async def test_arms_the_lock_even_when_the_fetched_content_matches_a_stub_already_seen(  # noqa: E501
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        previous = make_entity_revision(entity=_make_stub(), provider="text_pattern")
        mem_storage = make_mem_storage(
            external_credentials=[credential], nodes=[previous]
        )
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        cpf_fetcher = FakeCPFFetcher(
            revision=make_entity_revision(
                entity=_make_kipflow_graph(), provider="kipflow"
            )
        )
        mem_uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        first_result = await ExpandByCPF(
            uow_factory=mem_uow_factory,
            cpf_fetcher=cpf_fetcher,
            cpf=_CPF,
            username="alice",
        ).execute()

        assert first_result is not None

        with pytest.raises(AlreadyFetchedError):
            await ExpandByCPF(
                uow_factory=mem_uow_factory,
                cpf_fetcher=cpf_fetcher,
                cpf=_CPF,
                username="alice",
            ).execute()
