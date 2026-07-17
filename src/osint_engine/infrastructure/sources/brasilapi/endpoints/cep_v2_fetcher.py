from __future__ import annotations

from datetime import UTC, datetime
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import AsyncClient, HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.cep_fetcher import CEPFetcher
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.data_source_error import DataSourceRequestError
from osint_engine.infrastructure.sources.brasilapi.brasilapi_fetcher import (
    BrasilAPIFetcher,
)
from osint_engine.infrastructure.sources.brasilapi.endpoints.cep_v2_mapper import (
    map_address,
)
from osint_engine.infrastructure.sources.payload import Payload

if TYPE_CHECKING:
    from osint_engine.domain.entities.nodes.address import Address


class BrasilAPICEPv2Fetcher(BrasilAPIFetcher, CEPFetcher, url_suffix="cep/v2/"):
    @override
    def __init__(self, *, http_client: AsyncClient) -> None:
        super().__init__(http_client=http_client)

    @override
    async def fetch(self, cep: str, number: str, /) -> EntityRevision[Address]:
        self._logger.info("cep.fetch.start", cep=cep)

        try:
            response = await self._http_client.get(url=self._BASE_URL.join(url=cep))
            response.raise_for_status()

            data: dict[str, object] = response.json()

            fetched_at = datetime.now(tz=UTC)

            self._logger.info("cep.fetch.success", cep=cep)
        except HTTPStatusError as exception:
            self._logger.warning(
                "cep.fetch.error",
                cep=cep,
                status_code=exception.response.status_code,
            )

            raise DataSourceRequestError(
                source=self._SOURCE, status_code=exception.response.status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                "cep.fetch.error",
                cep=cep,
                exc_type=type(exception).__name__,
            )

            raise DataSourceRequestError(
                source=self._SOURCE, status_code=None
            ) from exception

        payload = Payload(source=self._SOURCE, data=data)

        return EntityRevision(
            entity=map_address(payload=payload, number=number),
            fetched_at=fetched_at,
            merged_at=None,
        )
