from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.fetchers.cnep_fetcher import CNEPFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ExpandByCNEP(Query[Graph]):
    uow_factory: Callable[[], UoW]
    cnep_fetcher: CNEPFetcher
    cpf_or_cnpj: str
    cnep_id: int | None
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        cnep_fetcher: CNEPFetcher,
        cpf_or_cnpj: str,
        cnep_id: int | None,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            cnep_fetcher=cnep_fetcher,
            cpf_or_cnpj=cpf_or_cnpj,
            cnep_id=cnep_id,
            username=username,
        )

    @override
    async def execute(self) -> Graph:
        _logger.info("cnep.expansion.start", cpf_or_cnpj=self.cpf_or_cnpj)

        async with self.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
            )

            if credential is None:
                raise ExternalCredentialNotFoundError(
                    username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
                )

            revision = await self.cnep_fetcher.fetch(
                cpf_or_cnpj=self.cpf_or_cnpj,
                cnep_id=self.cnep_id,
                credential=credential,
            )

            await uow.graphs.merge(revision=revision)

        _logger.info("cnep.expansion.success", cpf_or_cnpj=self.cpf_or_cnpj)

        return revision.entity
