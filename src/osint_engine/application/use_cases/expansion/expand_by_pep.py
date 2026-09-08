from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.consumption.ensure_entity_logged import (
    ensure_person_logged,
)
from osint_engine.application.consumption.entity_stub import person_stub
from osint_engine.application.consumption.guard_reuse_lock import (
    find_already_fetched_error,
)
from osint_engine.application.contracts.use_case import Query, UseCaseRegistry
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.contracts.fetchers.pep_fetcher import PEPFetcher
    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.errors.entity_fetch_error import EntityFetchError

_logger = get_logger()


class ExpandByPEP(Query[EntityRevision[Graph] | None]):
    uow_factory: Callable[[], UoW]
    pep_fetcher: PEPFetcher
    cpf: str
    force: bool
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        pep_fetcher: PEPFetcher,
        cpf: str,
        force: bool = False,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            pep_fetcher=pep_fetcher,
            cpf=cpf,
            force=force,
            username=username,
        )

    @override
    async def execute(self) -> EntityRevision[Graph] | None:
        _logger.info("pep.expansion.start", cpf=self.cpf, force=self.force)

        provider = UseCaseRegistry.billing_for(type(self)).provider
        requested_at = datetime.now(tz=UTC)
        to_raise: EntityFetchError | ExternalCredentialNotFoundError | None = None
        stored: EntityRevision[Graph] | None = None

        async with self.uow_factory() as uow:
            to_raise = await find_already_fetched_error(
                uow=uow,
                entity_id=person_stub(self.cpf).id,
                use_case=type(self),
                force=self.force,
                requested_at=requested_at,
                username=self.username,
            )

            if to_raise is not None:
                _logger.info("pep.expansion.already_fetched", cpf=self.cpf)

            credential: ExternalCredential | None = None

            if to_raise is None:
                credential = await uow.external_credentials.find(
                    username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
                )

                if credential is None:
                    to_raise = ExternalCredentialNotFoundError(
                        username=self.username, provider=Provider.PORTAL_TRANSPARENCIA
                    )

            if to_raise is None and credential is not None:
                revision = await self.pep_fetcher.fetch(
                    cpf=self.cpf, credential=credential
                )

                if revision is not None:
                    stored = await uow.graphs.merge(revision=revision)
                else:
                    _logger.info("pep.expansion.empty", cpf=self.cpf)

                await ensure_person_logged(
                    uow=uow,
                    cpf=self.cpf,
                    provider=provider,
                    username=self.username,
                    requested_at=requested_at,
                    revision=revision,
                )

        if to_raise is not None:
            raise to_raise

        if stored is not None:
            _logger.info("pep.expansion.success", cpf=self.cpf)

        return stored


UseCaseRegistry.register(ExpandByPEP, provider="pep", billable=False)
