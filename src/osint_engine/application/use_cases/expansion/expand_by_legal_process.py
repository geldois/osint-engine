from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.fetchers.legal_process_fetcher import (
        LegalProcessFetcher,
    )
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ExpandByLegalProcess(Query[EntityRevision[Graph] | None]):
    uow_factory: Callable[[], UoW]
    legal_process_fetcher: LegalProcessFetcher
    cpf_or_cnpj: str
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        legal_process_fetcher: LegalProcessFetcher,
        cpf_or_cnpj: str,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            legal_process_fetcher=legal_process_fetcher,
            cpf_or_cnpj=cpf_or_cnpj,
            username=username,
        )

    @override
    async def execute(self) -> EntityRevision[Graph] | None:
        _logger.info("legal_process.expansion.start", cpf_or_cnpj=self.cpf_or_cnpj)

        async with self.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.KIPFLOW
            )

            if credential is None:
                raise ExternalCredentialNotFoundError(
                    username=self.username, provider=Provider.KIPFLOW
                )

            revision = await self.legal_process_fetcher.fetch(
                cpf_or_cnpj=self.cpf_or_cnpj, credential=credential
            )

            if revision is None:
                _logger.info(
                    "legal_process.expansion.empty", cpf_or_cnpj=self.cpf_or_cnpj
                )

                return None

            stored = await uow.graphs.merge(revision=revision)

        _logger.info("legal_process.expansion.success", cpf_or_cnpj=self.cpf_or_cnpj)

        return stored
