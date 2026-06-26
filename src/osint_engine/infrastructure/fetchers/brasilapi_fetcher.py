from __future__ import annotations

from abc import abstractmethod
from json import JSONDecodeError
from typing import TYPE_CHECKING, final, override

from httpx2 import URL, AsyncClient, HTTPStatusError, RequestError
from structlog.stdlib import get_logger

from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
from osint_engine.infrastructure.errors.fetcher_error import (
    ExternalAPIFetcherError,
)
from osint_engine.infrastructure.fetchers.mappers.brasilapi_mapper import (
    BrasilAPICNPJMapper,
)
from osint_engine.infrastructure.fetchers.schemas.fetcher_schema import Schema

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.graph import Graph

logger = get_logger()


class _BrasilAPIFetcher:
    _BASE_URL: URL = URL("https://brasilapi.com.br/api/")
    _SOURCE: str = "brasilapi"

    @final
    def __init_subclass__(cls, *, url_suffix: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls._BASE_URL = cls._BASE_URL.join(url=url_suffix)

    @abstractmethod
    def __init__(self, *, http_client: AsyncClient) -> None:
        self._http_client = http_client
        self._logger = logger.bind(source=self._SOURCE)


class BrasilAPICNPJFetcher(_BrasilAPIFetcher, CNPJFetcher, url_suffix="cnpj/v1/"):
    @override
    def __init__(self, *, http_client: AsyncClient) -> None:
        super().__init__(http_client=http_client)

        self._mapper = BrasilAPICNPJMapper

    @override
    async def fetch(self, cnpj: str, /) -> Graph:
        self._logger.info(event="cnpj.fetch.start", cnpj=cnpj)

        try:
            response = await self._http_client.get(url=self._BASE_URL.join(url=cnpj))
            response.raise_for_status()

            data: dict[str, object] = response.json()

            self._logger.info(event="cnpj.fetch.success", cnpj=cnpj)
        except HTTPStatusError as exception:
            self._logger.warning(
                event="cnpj.fetch.error",
                cnpj=cnpj,
                status_code=exception.response.status_code,
            )

            raise ExternalAPIFetcherError(
                source=self._SOURCE, status_code=exception.response.status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                event="cnpj.fetch.error",
                cnpj=cnpj,
                exc_type=type(exception).__name__,
            )

            raise ExternalAPIFetcherError(
                source=self._SOURCE, status_code=None
            ) from exception

        schema = Schema(source=self._SOURCE, data=data)

        return self._mapper.map(schema=schema)
