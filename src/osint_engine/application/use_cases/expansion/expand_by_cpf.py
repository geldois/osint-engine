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
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.entity_fetch_error import (
    AlreadyFetchedError,
    EntityFetchError,
)
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()

_KIPFLOW_PROVIDER = "kipflow"


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

        stub = Person(
            age_range=None,
            birthdate=None,
            cpf=self.cpf,
            name=None,
            registration_date=None,
            registration_status=None,
        )
        requested_at = datetime.now(tz=UTC)
        to_raise: EntityFetchError | ExternalCredentialNotFoundError | None = None
        result: EntityRevision[Graph] | None = None

        async with self.uow_factory() as uow:
            if not self.force:
                revisions = await uow.nodes.list_revisions(id_=stub.id)
                previous = next(
                    (
                        revision
                        for revision in revisions
                        if revision.provider == _KIPFLOW_PROVIDER
                    ),
                    None,
                )

                if previous is not None:
                    _logger.info("cpf.expansion.already_fetched", cpf=self.cpf)

                    await uow.entity_records.save(
                        record=EntityRecord(
                            id=uuid4(),
                            entity_id=stub.id,
                            entity_ref=previous.ref,
                            outcome="already_fetched",
                            provider=_KIPFLOW_PROVIDER,
                            requested_at=requested_at,
                            username=self.username,
                        )
                    )

                    to_raise = AlreadyFetchedError(
                        entity_id=stub.id,
                        provider=_KIPFLOW_PROVIDER,
                        fetched_at=previous.fetched_at,
                    )

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
                            provider=_KIPFLOW_PROVIDER,
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
                        provider=_KIPFLOW_PROVIDER,
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
                        provider=_KIPFLOW_PROVIDER,
                    )

                    await uow.nodes.merge(revision=person_revision)

                    await uow.entity_records.save(
                        record=EntityRecord(
                            id=uuid4(),
                            entity_id=stub.id,
                            entity_ref=person_revision.ref,
                            outcome="expanded",
                            provider=_KIPFLOW_PROVIDER,
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
