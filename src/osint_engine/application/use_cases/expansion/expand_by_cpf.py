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

    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ExpandByCPF(Query[Graph]):
    uow_factory: Callable[[], UoW]
    cpf_fetcher: CPFFetcher
    cpf: str
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        cpf_fetcher: CPFFetcher,
        cpf: str,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory, cpf_fetcher=cpf_fetcher, cpf=cpf, username=username
        )

    @override
    async def execute(self) -> Graph:
        _logger.info("cpf.expansion.start", cpf=self.cpf)

        async with self.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
            )

            if credential is None:
                raise ExternalCredentialNotFoundError(
                    username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
                )

            revision = await self.cpf_fetcher.fetch(cpf=self.cpf, credential=credential)

            await uow.graphs.merge(revision=revision)

        _logger.info("cpf.expansion.success", cpf=self.cpf)

        return revision.entity
