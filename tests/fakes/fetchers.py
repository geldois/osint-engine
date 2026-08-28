from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.fetchers.ceaf_fetcher import CEAFFetcher
from osint_engine.application.contracts.fetchers.ceis_fetcher import CEISFetcher
from osint_engine.application.contracts.fetchers.cepim_fetcher import CEPIMFetcher
from osint_engine.application.contracts.fetchers.cnep_fetcher import CNEPFetcher
from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
from osint_engine.application.contracts.fetchers.legal_process_fetcher import (
    LegalProcessFetcher,
)
from osint_engine.application.contracts.fetchers.pep_fetcher import PEPFetcher

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph


class FakeCNPJFetcher(CNPJFetcher):
    def __init__(self, *, revision: EntityRevision[Graph]) -> None:
        self.revision = revision

    @override
    async def fetch(self, *, cnpj: str) -> EntityRevision[Graph]:
        return self.revision


class FakeCPFFetcher(CPFFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision


class FakeCEISFetcher(CEISFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cpf_or_cnpj: str, ceis_id: int | None, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision


class FakeCNEPFetcher(CNEPFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cpf_or_cnpj: str, cnep_id: int | None, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision


class FakeCEPIMFetcher(CEPIMFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cnpj: str, cepim_id: int | None, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision


class FakeCEAFFetcher(CEAFFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cpf: str, ceaf_id: int | None, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision


class FakePEPFetcher(PEPFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision


class FakeLegalProcessFetcher(LegalProcessFetcher):
    def __init__(self, *, revision: EntityRevision[Graph] | None) -> None:
        self.revision = revision

    @override
    async def fetch(
        self, *, cpf_or_cnpj: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        return self.revision
