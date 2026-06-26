from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from osint_engine.application.use_cases.expansion.expand_by_cnpj import ExpandByCNPJ
from osint_engine.config.container import Container, Fetchers, UseCases
from osint_engine.infrastructure.fetchers.brasilapi_fetcher import BrasilAPICNPJFetcher
from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
from osint_engine.infrastructure.persistence.mem.mem_uow import MemUoW

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.config.settings import Settings


def build_container(*, settings: Settings, http_client: AsyncClient) -> Container:
    fetchers = Fetchers(cnpj_fetcher=BrasilAPICNPJFetcher(http_client=http_client))

    mem_storage = MemStorage()

    def uow_factory_func() -> MemUoW:
        return MemUoW(mem_storage=mem_storage)

    uow_factory = uow_factory_func

    use_cases = UseCases(
        expand_by_cnpj=partial(
            ExpandByCNPJ, uow_factory=uow_factory, cnpj_fetcher=fetchers.cnpj_fetcher
        )
    )

    return Container(
        settings=settings,
        fetchers=fetchers,
        uow_factory=uow_factory,
        use_cases=use_cases,
    )
