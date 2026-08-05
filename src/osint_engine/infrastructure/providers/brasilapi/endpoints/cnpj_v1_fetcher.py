from __future__ import annotations

from datetime import UTC, datetime
from json import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import AsyncClient, HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.cnpj_fetcher import CNPJFetcher
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.provider_error import ProviderRequestError
from osint_engine.infrastructure.providers.brasilapi.brasilapi_fetcher import (
    BrasilAPIFetcher,
)
from osint_engine.infrastructure.providers.brasilapi.endpoints.cnpj_v1_mapper import (
    map_graph,
)
from osint_engine.infrastructure.providers.payload import Payload

if TYPE_CHECKING:
    from osint_engine.domain.entities.bases.graph import Graph


class BrasilAPICNPJv1Fetcher(BrasilAPIFetcher, CNPJFetcher, url_suffix="cnpj/v1/"):
    @override
    def __init__(self, *, http_client: AsyncClient) -> None:
        super().__init__(http_client=http_client)

    @override
    async def fetch(self, *, cnpj: str) -> EntityRevision[Graph]:
        self._logger.info("cnpj.fetch.start", cnpj=cnpj)

        try:
            response = await self._http_client.get(url=self._BASE_URL.join(url=cnpj))
            response.raise_for_status()

            data: dict[str, object] = response.json()

            fetched_at = datetime.now(tz=UTC)

            self._logger.info("cnpj.fetch.success", cnpj=cnpj)
        except HTTPStatusError as exception:
            self._logger.warning(
                "cnpj.fetch.error",
                cnpj=cnpj,
                status_code=exception.response.status_code,
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=exception.response.status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                "cnpj.fetch.error",
                cnpj=cnpj,
                exc_type=type(exception).__name__,
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=None
            ) from exception

        payload = Payload(provider=self._PROVIDER, data=data)

        return EntityRevision(
            entity=map_graph(payload=payload),
            fetched_at=fetched_at,
            merged_at=None,
            provider=self._PROVIDER,
        )
