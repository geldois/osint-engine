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

    from osint_engine.application.contracts.fetchers.ceaf_fetcher import CEAFFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ExpandByCEAF(Query[EntityRevision[Graph] | None]):
    uow_factory: Callable[[], UoW]
    ceaf_fetcher: CEAFFetcher
    cpf: str
    ceaf_id: int | None
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        ceaf_fetcher: CEAFFetcher,
        cpf: str,
        ceaf_id: int | None,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            ceaf_fetcher=ceaf_fetcher,
            cpf=cpf,
            ceaf_id=ceaf_id,
            username=username,
        )

    @override
    async def execute(self) -> EntityRevision[Graph] | None:
        _logger.info("ceaf.expansion.start", cpf=self.cpf)

        async with self.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
            )

            if credential is None:
                raise ExternalCredentialNotFoundError(
                    username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
                )

            revision = await self.ceaf_fetcher.fetch(
                cpf=self.cpf,
                ceaf_id=self.ceaf_id,
                credential=credential,
            )

            if revision is None:
                _logger.info("ceaf.expansion.empty", cpf=self.cpf)

                return None

            stored = await uow.graphs.merge(revision=revision)

        _logger.info("ceaf.expansion.success", cpf=self.cpf)

        return stored
