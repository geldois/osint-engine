from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, override
from uuid import uuid4

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.consumption.ensure_entity_logged import (
    ensure_person_logged,
)
from osint_engine.application.consumption.entity_record import EntityRecord
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
    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.uow import UoW
    from osint_engine.application.errors.entity_fetch_error import EntityFetchError

_logger = get_logger()


class ExpandByCPF(Query[EntityRevision[Graph] | None]):
    uow_factory: Callable[[], UoW]
    cpf_fetcher: CPFFetcher
    cpf: str
    force: bool
    username: str

    @override
    def __init__(
        self,
        *,
        uow_factory: Callable[[], UoW],
        cpf_fetcher: CPFFetcher,
        cpf: str,
        force: bool = False,
        username: str,
    ) -> None:
        super().__init__(
            uow_factory=uow_factory,
            cpf_fetcher=cpf_fetcher,
            cpf=cpf,
            force=force,
            username=username,
        )

    @override
    async def execute(self) -> EntityRevision[Graph] | None:
        _logger.info("cpf.expansion.start", cpf=self.cpf, force=self.force)

        stub = person_stub(self.cpf)
        provider = UseCaseRegistry.billing_for(type(self)).provider
        requested_at = datetime.now(tz=UTC)
        to_raise: EntityFetchError | ExternalCredentialNotFoundError | None = None
        result: EntityRevision[Graph] | None = None

        async with self.uow_factory() as uow:
            to_raise = await find_already_fetched_error(
                uow=uow,
                entity_id=stub.id,
                use_case=type(self),
                force=self.force,
                requested_at=requested_at,
                username=self.username,
            )

            if to_raise is not None:
                _logger.info("cpf.expansion.already_fetched", cpf=self.cpf)

            credential: ExternalCredential | None = None

            if to_raise is None:
                credential = await uow.external_credentials.find(
                    username=self.username, provider=Provider.KIPFLOW
                )

                if credential is None:
                    await uow.entity_records.save(
                        record=EntityRecord(
                            id=uuid4(),
                            entity_id=stub.id,
                            entity_ref=None,
                            outcome="failed",
                            provider=provider,
                            requested_at=requested_at,
                            username=self.username,
                        )
                    )

                    to_raise = ExternalCredentialNotFoundError(
                        username=self.username, provider=Provider.KIPFLOW
                    )

            if to_raise is None and credential is not None:
                revision = await self.cpf_fetcher.fetch(
                    cpf=self.cpf, credential=credential
                )

                if revision is None:
                    _logger.info("cpf.expansion.empty", cpf=self.cpf)

                    await ensure_person_logged(
                        uow=uow,
                        cpf=self.cpf,
                        provider=provider,
                        username=self.username,
                        requested_at=requested_at,
                        revision=None,
                    )
                else:
                    stored = await uow.graphs.merge(revision=revision)

                    person = next(
                        node for node in revision.entity.nodes if node.id == stub.id
                    )
                    person_revision = EntityRevision(
                        entity=person,
                        fetched_at=revision.fetched_at,
                        merged_at=None,
                        provider=provider,
                    )

                    await uow.nodes.merge(revision=person_revision)

                    await uow.entity_records.save(
                        record=EntityRecord(
                            id=uuid4(),
                            entity_id=stub.id,
                            entity_ref=person_revision.ref,
                            outcome="expanded",
                            provider=provider,
                            requested_at=requested_at,
                            username=self.username,
                        )
                    )

                    result = stored

        if to_raise is not None:
            raise to_raise

        if result is not None:
            _logger.info("cpf.expansion.success", cpf=self.cpf)

        return result


UseCaseRegistry.register(ExpandByCPF, provider="kipflow", billable=True)
