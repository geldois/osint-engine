from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.consumption.ensure_entity_logged import (
    ensure_company_logged,
    ensure_person_logged,
)
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.fetchers.cnep_fetcher import CNEPFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()

_PROVIDER = "cnep"
_CPF_DIGIT_LENGTH = 11


class ExpandByCNEP(Query[EntityRevision[Graph] | None]):
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
    async def execute(self) -> EntityRevision[Graph] | None:
        _logger.info("cnep.expansion.start", cpf_or_cnpj=self.cpf_or_cnpj)

        requested_at = datetime.now(tz=UTC)
        stored: EntityRevision[Graph] | None = None

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

            if revision is not None:
                stored = await uow.graphs.merge(revision=revision)
            else:
                _logger.info("cnep.expansion.empty", cpf_or_cnpj=self.cpf_or_cnpj)

            if len(self.cpf_or_cnpj) == _CPF_DIGIT_LENGTH:
                await ensure_person_logged(
                    uow=uow,
                    cpf=self.cpf_or_cnpj,
                    provider=_PROVIDER,
                    username=self.username,
                    requested_at=requested_at,
                    revision=revision,
                )
            else:
                await ensure_company_logged(
                    uow=uow,
                    cnpj=self.cpf_or_cnpj,
                    provider=_PROVIDER,
                    username=self.username,
                    requested_at=requested_at,
                    revision=revision,
                )

        if stored is not None:
            _logger.info("cnep.expansion.success", cpf_or_cnpj=self.cpf_or_cnpj)

        return stored
