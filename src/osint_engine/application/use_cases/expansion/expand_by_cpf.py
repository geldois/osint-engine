from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.auth.external_credential import Provider
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.errors.entity_fetch_error import AlreadyFetchedError
from osint_engine.application.errors.external_credential_error import (
    ExternalCredentialNotFoundError,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.domain.entities.nodes.person import Person

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()

_KIPFLOW_PROVIDER = "kipflow"


class ExpandByCPF(Query[Graph | None]):
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
    async def execute(self) -> Graph | None:
        _logger.info("cpf.expansion.start", cpf=self.cpf, force=self.force)

        stub = Person(
            age_range=None,
            birthdate=None,
            cpf=self.cpf,
            name=None,
            registration_date=None,
            registration_status=None,
        )

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

                    raise AlreadyFetchedError(
                        entity_id=stub.id,
                        provider=_KIPFLOW_PROVIDER,
                        fetched_at=previous.fetched_at,
                    )

            credential = await uow.external_credentials.find(
                username=self.username, provider=Provider.KIPFLOW
            )

            if credential is None:
                raise ExternalCredentialNotFoundError(
                    username=self.username, provider=Provider.KIPFLOW
                )

            revision = await self.cpf_fetcher.fetch(cpf=self.cpf, credential=credential)

            if revision is None:
                _logger.info("cpf.expansion.empty", cpf=self.cpf)

                return None

            await uow.graphs.merge(revision=revision)

            person = next(node for node in revision.entity.nodes if node.id == stub.id)

            await uow.nodes.merge(
                revision=EntityRevision(
                    entity=person,
                    fetched_at=revision.fetched_at,
                    merged_at=None,
                    provider=_KIPFLOW_PROVIDER,
                )
            )

        _logger.info("cpf.expansion.success", cpf=self.cpf)

        return revision.entity
