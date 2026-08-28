from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.consumption.ensure_entity_logged import (
    ensure_company_logged,
)
from osint_engine.application.contracts.use_case import Query
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()

_PROVIDER = "brasilapi"
_ANONYMOUS_USERNAME = "anonymous"


class ExpandByCNPJ(Query[EntityRevision[Graph]]):
    uow_factory: Callable[[], UoW]
    cnpj_fetcher: CNPJFetcher
    cnpj: str

    @override
    def __init__(
        self, *, uow_factory: Callable[[], UoW], cnpj_fetcher: CNPJFetcher, cnpj: str
    ) -> None:
        super().__init__(uow_factory=uow_factory, cnpj_fetcher=cnpj_fetcher, cnpj=cnpj)

    @override
    async def execute(self) -> EntityRevision[Graph]:
        _logger.info("cnpj.expansion.start", cnpj=self.cnpj)

        requested_at = datetime.now(tz=UTC)

        async with self.uow_factory() as uow:
            revision = await self.cnpj_fetcher.fetch(cnpj=self.cnpj)

            stored = await uow.graphs.merge(revision=revision)

            await ensure_company_logged(
                uow=uow,
                cnpj=self.cnpj,
                provider=_PROVIDER,
                username=_ANONYMOUS_USERNAME,
                requested_at=requested_at,
                revision=revision,
            )

        _logger.info("cnpj.expansion.success", cnpj=self.cnpj)

        return stored
