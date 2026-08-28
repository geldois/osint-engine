from __future__ import annotations

from datetime import UTC, datetime
from functools import reduce
from json import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.legal_process_fetcher import (
    LegalProcessFetcher,
)
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.provider_error import (
    InsufficientCreditsError,
    ProviderRequestError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.providers.kipflow.endpoints.legal_process_mapper import (  # noqa: E501
    map_graph,
)
from osint_engine.infrastructure.providers.kipflow.kipflow_fetcher import KipFlowFetcher
from osint_engine.infrastructure.providers.payload import Payload

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.application.contracts.services.kipflow_rate_limiter import (
        KipFlowRateLimiter,
    )
    from osint_engine.domain.entities.bases.graph import Graph

_CPF_LENGTH = 11
_INSUFFICIENT_CREDITS_STATUS = 402


class KipFlowLegalProcessFetcher(
    KipFlowFetcher, LegalProcessFetcher, url_suffix="legal/v1/parties/"
):
    @override
    def __init__(
        self, *, http_client: AsyncClient, rate_limiter: KipFlowRateLimiter
    ) -> None:
        super().__init__(http_client=http_client)
        self._rate_limiter = rate_limiter

    @override
    async def fetch(
        self, *, cpf_or_cnpj: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self._logger.info("legal_process.fetch.start", cpf_or_cnpj=cpf_or_cnpj)

        await self._rate_limiter.acquire(credential=credential)

        document_kind = "cpf" if len(cpf_or_cnpj) == _CPF_LENGTH else "cnpj"

        try:
            headers = self._build_headers(credential=credential)
            url = self._BASE_URL.join(url=document_kind)
            params = {"q": cpf_or_cnpj}

            response = await self._http_client.get(
                url=url, params=params, headers=headers
            )
            response.raise_for_status()

            data: dict[str, object] = response.json()

            fetched_at = datetime.now(tz=UTC)

            self._logger.info("legal_process.fetch.success", cpf_or_cnpj=cpf_or_cnpj)
        except HTTPStatusError as exception:
            status_code = exception.response.status_code

            self._logger.warning(
                "legal_process.fetch.error",
                cpf_or_cnpj=cpf_or_cnpj,
                status_code=status_code,
            )

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
                "legal_process.fetch.error",
                cpf_or_cnpj=cpf_or_cnpj,
                exc_type=type(exception).__name__,
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=None
            ) from exception

        payload = Payload(provider=self._PROVIDER, data=data)

        if not payload.require(key="success", expected_type=bool):
            raise UnexpectedPayloadError(provider=self._PROVIDER, missing_field="data")

        records = payload.require(key="data", expected_type=list[dict[str, object]])

        if not records:
            return None

        graphs = (
            map_graph(
                cpf_or_cnpj=cpf_or_cnpj,
                payload=payload.scope(data=record),
            )
            for record in records
        )
        graph = reduce(
            lambda merged, next_graph: merged.merge(other=next_graph), graphs
        )

        return EntityRevision(
            entity=graph, fetched_at=fetched_at, merged_at=None, provider=self._PROVIDER
        )
