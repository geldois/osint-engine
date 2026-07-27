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

    from osint_engine.application.contracts.fetchers.ceis_fetcher import CEISFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ExpandByCEIS(Query[Graph | None]):
    uow_factory: Callable[[], UoW]
    ceis_fetcher: CEISFetcher
    cpf_or_cnpj: str
    ceis_id: int | None
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        ceis_fetcher: CEISFetcher,
        cpf_or_cnpj: str,
        ceis_id: int | None,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            ceis_fetcher=ceis_fetcher,
            cpf_or_cnpj=cpf_or_cnpj,
            ceis_id=ceis_id,
            username=username,
        )

    @override
    async def execute(self) -> Graph | None:
        _logger.info("ceis.expansion.start", cpf_or_cnpj=self.cpf_or_cnpj)

        async with self.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
            )

            if credential is None:
                raise ExternalCredentialNotFoundError(
                    username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
                )

            revision = await self.ceis_fetcher.fetch(
                cpf_or_cnpj=self.cpf_or_cnpj,
                ceis_id=self.ceis_id,
                credential=credential,
            )

            if revision is None:
                _logger.info("ceis.expansion.empty", cpf_or_cnpj=self.cpf_or_cnpj)

                return None

            await uow.graphs.merge(revision=revision)

        _logger.info("ceis.expansion.success", cpf_or_cnpj=self.cpf_or_cnpj)

        return revision.entity
