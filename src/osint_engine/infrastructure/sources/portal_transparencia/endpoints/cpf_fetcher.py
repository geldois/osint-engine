from __future__ import annotations

from datetime import UTC, datetime
from json import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import URL, AsyncClient, HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.cpf_fetcher import CPFFetcher
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.data_source_error import DataSourceRequestError
from osint_engine.infrastructure.sources.payload import Payload
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cpf_mapper import (  # noqa: E501
    map_graph,
)
from osint_engine.infrastructure.sources.portal_transparencia.portal_transparencia_fetcher import (  # noqa: E501
    PortalTransparenciaFetcher,
)

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.domain.entities.bases.graph import Graph


class PortalTransparenciaCPFFetcher(
    PortalTransparenciaFetcher, CPFFetcher, url_suffix="pf"
):
    # No trailing slash, unlike "cnep/"/"ceis/": this endpoint is always
    # query-param based (never joined with a further path segment), and the
    # real API 403s on a trailing slash before "?" — see cnep_fetcher.py's
    # `.removesuffix("/")` workaround for that same failure mode.
    @override
    def __init__(self, *, http_client: AsyncClient) -> None:
        super().__init__(http_client=http_client)

    @override
    async def fetch(
        self, *, cpf: str, credential: ExternalCredential
    ) -> EntityRevision[Graph]:
        self._logger.info("cpf.fetch.start", cpf=cpf)

        try:
            headers = self._build_headers(credential=credential)
            url = URL(str(self._BASE_URL))
            params = {"cpf": cpf}

            response = await self._http_client.get(
                url=url, params=params, headers=headers
            )
            response.raise_for_status()

            data: dict[str, object] = response.json()

            fetched_at = datetime.now(tz=UTC)

            self._logger.info("cpf.fetch.success", cpf=cpf)
        except HTTPStatusError as exception:
            self._logger.warning(
                "cpf.fetch.error", cpf=cpf, status_code=exception.response.status_code
            )

            self._raise_for_credential_rejection(
                exception=exception, credential=credential
            )

            raise DataSourceRequestError(
                source=self._SOURCE, status_code=exception.response.status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                "cpf.fetch.error", cpf=cpf, exc_type=type(exception).__name__
            )

            raise DataSourceRequestError(
                source=self._SOURCE, status_code=None
            ) from exception

        payload = Payload(source=self._SOURCE, data=data)

        return EntityRevision(
            entity=map_graph(payload=payload), fetched_at=fetched_at, merged_at=None
        )
