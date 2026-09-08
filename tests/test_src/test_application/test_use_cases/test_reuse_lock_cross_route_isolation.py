from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError
from osint_engine.application.use_cases.expansion.expand_by_ceaf import ExpandByCEAF
from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
from osint_engine.application.use_cases.expansion.expand_by_legal_process import (
    ExpandByLegalProcess,
)
from osint_engine.application.use_cases.expansion.expand_by_pep import ExpandByPEP
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from tests.conftest import (
        MakeEntityRevision,
        MakeExternalCredential,
        MakeGraph,
        MakeMemStorage,
        MakeMemUoW,
    )
    from tests.test_src.test_application.conftest import (
        MakeFakeCEAFFetcher,
        MakeFakeCPFFetcher,
        MakeFakeLegalProcessFetcher,
        MakeFakePEPFetcher,
        MakeMemUoWFactory,
    )

_CPF = "10000000000"


def _make_kipflow_graph() -> Graph:
    person = Person(
        age_range=None,
        birthdate=None,
        cpf=_CPF,
        name=None,
        registration_date=None,
        registration_status=None,
    )

    return Graph(edges=frozenset(), nodes=frozenset({person}), root_id=person.id)


class TestPortalTransparenciaRoutesStayIsolated:
    @pytest.mark.asyncio
    async def test_ceaf_then_pep_then_ceaf_again_still_arms_the_ceaf_lock(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_ceaf_fetcher: MakeFakeCEAFFetcher,
        make_fake_pep_fetcher: MakeFakePEPFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.PORTAL_TRANSPARENCIA
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        mem_uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        ceaf_result = await ExpandByCEAF(
            uow_factory=mem_uow_factory,
            ceaf_fetcher=make_fake_ceaf_fetcher(
                revision=make_entity_revision(entity=make_graph())
            ),
            cpf=_CPF,
            ceaf_id=None,
            username="alice",
        ).execute()

        assert ceaf_result is not None

        pep_result = await ExpandByPEP(
            uow_factory=mem_uow_factory,
            pep_fetcher=make_fake_pep_fetcher(
                revision=make_entity_revision(entity=make_graph())
            ),
            cpf=_CPF,
            username="alice",
        ).execute()

        assert pep_result is not None

        with pytest.raises(AlreadyFetchedError) as exception:
            await ExpandByCEAF(
                uow_factory=mem_uow_factory,
                ceaf_fetcher=make_fake_ceaf_fetcher(
                    revision=make_entity_revision(entity=make_graph())
                ),
                cpf=_CPF,
                ceaf_id=None,
                username="alice",
            ).execute()

        assert exception.value.provider == "ceaf"

    @pytest.mark.asyncio
    async def test_pep_then_ceaf_then_pep_again_still_arms_the_pep_lock(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_ceaf_fetcher: MakeFakeCEAFFetcher,
        make_fake_pep_fetcher: MakeFakePEPFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.PORTAL_TRANSPARENCIA
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        mem_uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        pep_result = await ExpandByPEP(
            uow_factory=mem_uow_factory,
            pep_fetcher=make_fake_pep_fetcher(
                revision=make_entity_revision(entity=make_graph())
            ),
            cpf=_CPF,
            username="alice",
        ).execute()

        assert pep_result is not None

        ceaf_result = await ExpandByCEAF(
            uow_factory=mem_uow_factory,
            ceaf_fetcher=make_fake_ceaf_fetcher(
                revision=make_entity_revision(entity=make_graph())
            ),
            cpf=_CPF,
            ceaf_id=None,
            username="alice",
        ).execute()

        assert ceaf_result is not None

        with pytest.raises(AlreadyFetchedError) as exception:
            await ExpandByPEP(
                uow_factory=mem_uow_factory,
                pep_fetcher=make_fake_pep_fetcher(
                    revision=make_entity_revision(entity=make_graph())
                ),
                cpf=_CPF,
                username="alice",
            ).execute()

        assert exception.value.provider == "pep"


class TestKipFlowRoutesStayIsolated:
    @pytest.mark.asyncio
    async def test_cpf_root_then_legal_process_then_cpf_root_again_still_arms_the_lock(
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_cpf_fetcher: MakeFakeCPFFetcher,
        make_fake_legal_process_fetcher: MakeFakeLegalProcessFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        mem_uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        cpf_result = await ExpandByCPF(
            uow_factory=mem_uow_factory,
            cpf_fetcher=make_fake_cpf_fetcher(
                revision=make_entity_revision(entity=_make_kipflow_graph())
            ),
            cpf=_CPF,
            username="alice",
        ).execute()

        assert cpf_result is not None

        legal_process_result = await ExpandByLegalProcess(
            uow_factory=mem_uow_factory,
            legal_process_fetcher=make_fake_legal_process_fetcher(
                revision=make_entity_revision(entity=make_graph())
            ),
            cpf_or_cnpj=_CPF,
            username="alice",
        ).execute()

        assert legal_process_result is not None

        with pytest.raises(AlreadyFetchedError) as exception:
            await ExpandByCPF(
                uow_factory=mem_uow_factory,
                cpf_fetcher=make_fake_cpf_fetcher(
                    revision=make_entity_revision(entity=make_graph())
                ),
                cpf=_CPF,
                username="alice",
            ).execute()

        assert exception.value.provider == "kipflow"

    @pytest.mark.asyncio
    async def test_legal_process_then_cpf_root_then_legal_process_again_still_arms_the_lock(  # noqa: E501
        self,
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_fake_cpf_fetcher: MakeFakeCPFFetcher,
        make_fake_legal_process_fetcher: MakeFakeLegalProcessFetcher,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credential = make_external_credential(
            username="alice", provider=Provider.KIPFLOW
        )
        mem_storage = make_mem_storage(external_credentials=[credential])
        mem_uow = make_mem_uow(mem_storage=mem_storage)
        mem_uow_factory = make_mem_uow_factory(mem_uow=mem_uow)

        legal_process_result = await ExpandByLegalProcess(
            uow_factory=mem_uow_factory,
            legal_process_fetcher=make_fake_legal_process_fetcher(
                revision=make_entity_revision(entity=make_graph())
            ),
            cpf_or_cnpj=_CPF,
            username="alice",
        ).execute()

        assert legal_process_result is not None

        cpf_result = await ExpandByCPF(
            uow_factory=mem_uow_factory,
            cpf_fetcher=make_fake_cpf_fetcher(
                revision=make_entity_revision(entity=_make_kipflow_graph())
            ),
            cpf=_CPF,
            username="alice",
        ).execute()

        assert cpf_result is not None

        with pytest.raises(AlreadyFetchedError) as exception:
            await ExpandByLegalProcess(
                uow_factory=mem_uow_factory,
                legal_process_fetcher=make_fake_legal_process_fetcher(
                    revision=make_entity_revision(entity=make_graph())
                ),
                cpf_or_cnpj=_CPF,
                username="alice",
            ).execute()

        assert exception.value.provider == "legal_process"
