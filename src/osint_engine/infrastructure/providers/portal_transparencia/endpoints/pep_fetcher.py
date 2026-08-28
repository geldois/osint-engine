from __future__ import annotations

from datetime import UTC, datetime
from functools import reduce
from json import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.pep_fetcher import PEPFetcher
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.provider_error import ProviderRequestError
from osint_engine.infrastructure.providers.payload import Payload
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.pep_mapper import (  # noqa: E501
    map_graph,
)
from osint_engine.infrastructure.providers.portal_transparencia.portal_transparencia_fetcher import (  # noqa: E501
    PortalTransparenciaFetcher,
)

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.domain.entities.bases.graph import Graph


class PortalTransparenciaPEPFetcher(
    PortalTransparenciaFetcher, PEPFetcher, url_suffix="peps"
):
    @override
    def __init__(self, *, http_client: AsyncClient) -> None:
        super().__init__(http_client=http_client)

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self._logger.info("pep.fetch.start", cpf=cpf)

        try:
            headers = self._build_headers(credential=credential)
            params = {"cpf": cpf, "pagina": "1"}

            response = await self._http_client.get(
                url=self._BASE_URL, params=params, headers=headers
            )
            response.raise_for_status()

            records: list[dict[str, object]] = response.json()

            fetched_at = datetime.now(tz=UTC)

            self._logger.info("pep.fetch.success", cpf=cpf)
        except HTTPStatusError as exception:
            self._logger.warning(
                "pep.fetch.error", cpf=cpf, status_code=exception.response.status_code
            )

            self._raise_for_credential_rejection(
                exception=exception, credential=credential
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=exception.response.status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                "pep.fetch.error", cpf=cpf, exc_type=type(exception).__name__
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=None
            ) from exception

        if not records:
            return None

        graphs = (
            map_graph(payload=Payload(provider=self._PROVIDER, data=record))
            for record in records
        )
        graph = reduce(
            lambda merged, next_graph: merged.merge(other=next_graph), graphs
        )

        return EntityRevision(
            entity=graph, fetched_at=fetched_at, merged_at=None, provider=self._PROVIDER
        )
