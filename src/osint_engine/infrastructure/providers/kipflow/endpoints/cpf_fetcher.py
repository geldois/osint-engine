from __future__ import annotations

from datetime import UTC, datetime
from json import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import AsyncClient, HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.provider_error import (
    InsufficientCreditsError,
    ProviderRequestError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.providers.kipflow.endpoints.cpf_mapper import map_graph
from osint_engine.infrastructure.providers.kipflow.kipflow_fetcher import KipFlowFetcher
from osint_engine.infrastructure.providers.payload import Payload

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.contracts.services.kipflow_rate_limiter import (
        KipFlowRateLimiter,
    )
    from osint_engine.domain.entities.bases.graph import Graph

_NOT_FOUND_STATUS = 404
_INSUFFICIENT_CREDITS_STATUS = 402


class KipFlowCPFFetcher(KipFlowFetcher, CPFFetcher, url_suffix="people/v1/search"):
    @override
    def __init__(
        self, *, http_client: AsyncClient, rate_limiter: KipFlowRateLimiter
    ) -> None:
        super().__init__(http_client=http_client)
        self._rate_limiter = rate_limiter

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self._logger.info("cpf.fetch.start", cpf=cpf)

        await self._rate_limiter.acquire(credential=credential)

        try:
            headers = self._build_headers(credential=credential)
            params = {"cpf": cpf, "datasets": "basic,registration_status"}

            response = await self._http_client.get(
                url=self._BASE_URL, params=params, headers=headers
            )

            if response.status_code == _NOT_FOUND_STATUS:
                self._logger.info("cpf.fetch.not_found", cpf=cpf)

                return None

            response.raise_for_status()

            data: dict[str, object] = response.json()
            fetched_at = datetime.now(tz=UTC)

            self._logger.info("cpf.fetch.success", cpf=cpf)
        except HTTPStatusError as exception:
            status_code = exception.response.status_code

            self._logger.warning("cpf.fetch.error", cpf=cpf, status_code=status_code)

            self._raise_for_credential_rejection(
                exception=exception, credential=credential
            )

            if status_code == _INSUFFICIENT_CREDITS_STATUS:
                raise InsufficientCreditsError(provider=self._PROVIDER) from exception

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                "cpf.fetch.error", cpf=cpf, exc_type=type(exception).__name__
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=None
            ) from exception

        payload = Payload(provider=self._PROVIDER, data=data)

        if not payload.require(key="success", expected_type=bool):
            raise UnexpectedPayloadError(provider=self._PROVIDER, missing_field="data")

        return EntityRevision(
            entity=map_graph(
                payload=payload.scope(
                    data=payload.require(key="data", expected_type=dict[str, object])
                )
            ),
            fetched_at=fetched_at,
            merged_at=None,
            provider=self._PROVIDER,
        )
