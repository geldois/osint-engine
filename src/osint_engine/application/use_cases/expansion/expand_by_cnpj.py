from __future__ import annotations

from typing import TYPE_CHECKING, override

from structlog.stdlib import get_logger

from osint_engine.application.contracts.use_case import Query
from osint_engine.domain.entities.bases.graph import Graph

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
    from osint_engine.application.contracts.uow import UoW

_logger = get_logger()


class ExpandByCNPJ(Query[Graph]):
    uow_factory: Callable[[], UoW]
    cnpj_fetcher: CNPJFetcher
    cnpj: str

    @override
    def __init__(
        self, *, uow_factory: Callable[[], UoW], cnpj_fetcher: CNPJFetcher, cnpj: str
    ) -> None:
        super().__init__(uow_factory=uow_factory, cnpj_fetcher=cnpj_fetcher, cnpj=cnpj)

    @override
    async def execute(self) -> Graph:
        _logger.info("cnpj.expansion.start", cnpj=self.cnpj)

        async with self.uow_factory() as uow:
            graph = await self.cnpj_fetcher.fetch(self.cnpj)

            await uow.graphs.save(graph=graph)

        _logger.info("cnpj.expansion.success", cnpj=self.cnpj)

        return graph
