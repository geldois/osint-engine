from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import pytest

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError
from osint_engine.application.use_cases.expansion.expand_by_ceaf import ExpandByCEAF
from osint_engine.application.use_cases.expansion.expand_by_ceis import ExpandByCEIS
from osint_engine.application.use_cases.expansion.expand_by_cepim import ExpandByCEPIM
from osint_engine.application.use_cases.expansion.expand_by_cnep import ExpandByCNEP
from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
from osint_engine.application.use_cases.expansion.expand_by_legal_process import (
    ExpandByLegalProcess,
)
from osint_engine.application.use_cases.expansion.expand_by_pep import ExpandByPEP
from osint_engine.domain.entities.graphs import CompositeGraph
from osint_engine.domain.entities.nodes import Person
from tests.fakes.fetchers import (
    FakeCEAFFetcher,
    FakeCEISFetcher,
    FakeCEPIMFetcher,
    FakeCNEPFetcher,
    FakeCPFFetcher,
    FakeLegalProcessFetcher,
    FakePEPFetcher,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.revision.entity_revision import EntityRevision
    from tests.fixtures.application import MakeEntityRevision, MakeExternalCredential
    from tests.fixtures.domain import MakeGraph
    from tests.fixtures.persistence import MakeMemStorage, MakeMemUoW, MakeMemUoWFactory

_CPF = "10000000000"
_CNPJ = "10000000000000"


def _person_graph() -> CompositeGraph:
    person = Person(
        age_range=None,
        birthdate=None,
        cpf=_CPF,
        name=None,
        registration_date=None,
        registration_status=None,
    )

    return CompositeGraph(
        edges=frozenset(), nodes=frozenset({person}), root_id=person.id
    )


class _Executable(Protocol):
    async def execute(self) -> object: ...


type _UoWFactory = Callable[[], UoW]
type _Revision = EntityRevision[CompositeGraph]


def _ceaf(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByCEAF(
        uow_factory=uow,
        ceaf_fetcher=FakeCEAFFetcher(revision=revision),
        cpf=_CPF,
        ceaf_id=None,
        username=username,
    )


def _ceis(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByCEIS(
        uow_factory=uow,
        ceis_fetcher=FakeCEISFetcher(revision=revision),
        cpf_or_cnpj=_CPF,
        ceis_id=None,
        username=username,
    )


def _cepim(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByCEPIM(
        uow_factory=uow,
        cepim_fetcher=FakeCEPIMFetcher(revision=revision),
        cnpj=_CNPJ,
        cepim_id=None,
        username=username,
    )


def _cnep(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByCNEP(
        uow_factory=uow,
        cnep_fetcher=FakeCNEPFetcher(revision=revision),
        cpf_or_cnpj=_CPF,
        cnep_id=None,
        username=username,
    )


def _pep(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByPEP(
        uow_factory=uow,
        pep_fetcher=FakePEPFetcher(revision=revision),
        cpf=_CPF,
        username=username,
    )


def _cpf(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByCPF(
        uow_factory=uow,
        cpf_fetcher=FakeCPFFetcher(revision=revision),
        cpf=_CPF,
        username=username,
    )


def _legal_process(uow: _UoWFactory, revision: _Revision, username: str) -> _Executable:
    return ExpandByLegalProcess(
        uow_factory=uow,
        legal_process_fetcher=FakeLegalProcessFetcher(revision=revision),
        cpf_or_cnpj=_CPF,
        username=username,
    )


type _Build = Callable[[_UoWFactory, _Revision, str], _Executable]

_CASES = [
    pytest.param(Provider.PORTAL_TRANSPARENCIA, _ceaf, False, id="ceaf"),
    pytest.param(Provider.PORTAL_TRANSPARENCIA, _ceis, False, id="ceis"),
    pytest.param(Provider.PORTAL_TRANSPARENCIA, _cepim, False, id="cepim"),
    pytest.param(Provider.PORTAL_TRANSPARENCIA, _cnep, False, id="cnep"),
    pytest.param(Provider.PORTAL_TRANSPARENCIA, _pep, False, id="pep"),
    pytest.param(Provider.KIPFLOW, _cpf, True, id="cpf"),
    pytest.param(Provider.KIPFLOW, _legal_process, False, id="legal_process"),
]


class TestReuseLockIsPerUser:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(("provider", "build", "person_root"), _CASES)
    async def test_one_users_expansion_never_blocks_another_users_first_expansion(
        self,
        provider: Provider,
        build: _Build,
        person_root: bool,  # noqa: FBT001
        make_entity_revision: MakeEntityRevision,
        make_external_credential: MakeExternalCredential,
        make_graph: MakeGraph,
        make_mem_storage: MakeMemStorage,
        make_mem_uow: MakeMemUoW,
        make_mem_uow_factory: MakeMemUoWFactory,
    ) -> None:
        credentials = [
            make_external_credential(username=username, provider=provider)
            for username in ("alice", "bob")
        ]
        mem_storage = make_mem_storage(external_credentials=credentials)
        uow_factory = make_mem_uow_factory(
            mem_uow=make_mem_uow(mem_storage=mem_storage)
        )
        graph = _person_graph() if person_root else make_graph()
        revision = make_entity_revision(entity=graph)

        await build(uow_factory, revision, "alice").execute()

        with pytest.raises(AlreadyFetchedError):
            await build(uow_factory, revision, "alice").execute()

        bob_result = await build(uow_factory, revision, "bob").execute()

        assert bob_result is not None
