from __future__ import annotations

from datetime import UTC, datetime
from functools import reduce
from json import JSONDecodeError
from typing import TYPE_CHECKING, override

from httpx2 import URL, AsyncClient, HTTPStatusError, RequestError

from osint_engine.application.contracts.fetchers.ceis_fetcher import CEISFetcher
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.infrastructure.errors.provider_error import ProviderRequestError
from osint_engine.infrastructure.providers.payload import Payload
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.ceis_mapper import (  # noqa: E501
    map_graph,
)
from osint_engine.infrastructure.providers.portal_transparencia.portal_transparencia_fetcher import (  # noqa: E501
    PortalTransparenciaFetcher,
)

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from osint_engine.domain.entities.bases.graph import Graph


class PortalTransparenciaCEISFetcher(
    PortalTransparenciaFetcher, CEISFetcher, url_suffix="ceis/"
):
    @override
    def __init__(self, *, http_client: AsyncClient) -> None:
        super().__init__(http_client=http_client)

    @override
    async def fetch(
        self, *, cpf_or_cnpj: str, ceis_id: int | None, credential: ExternalCredential
    ) -> EntityRevision[Graph] | None:
        self._logger.info("ceis.fetch.start", cpf_or_cnpj=cpf_or_cnpj, ceis_id=ceis_id)

        try:
            headers = self._build_headers(credential=credential)

            if ceis_id is None:
                url = URL(str(self._BASE_URL).removesuffix("/"))
                params = {"codigoSancionado": cpf_or_cnpj, "pagina": "1"}
            else:
                url = self._BASE_URL.join(url=str(ceis_id))
                params = None

            response = await self._http_client.get(
                url=url, params=params, headers=headers
            )
            response.raise_for_status()

            raw = response.json()

            fetched_at = datetime.now(tz=UTC)

            self._logger.info(
                "ceis.fetch.success", cpf_or_cnpj=cpf_or_cnpj, ceis_id=ceis_id
            )
        except HTTPStatusError as exception:
            self._logger.warning(
                "ceis.fetch.error",
                cpf_or_cnpj=cpf_or_cnpj,
                ceis_id=ceis_id,
                status_code=exception.response.status_code,
            )

            self._raise_for_credential_rejection(
                exception=exception, credential=credential
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=exception.response.status_code
            ) from exception
        except (RequestError, JSONDecodeError) as exception:
            self._logger.exception(
                "ceis.fetch.error",
                cpf_or_cnpj=cpf_or_cnpj,
                ceis_id=ceis_id,
                exc_type=type(exception).__name__,
            )

            raise ProviderRequestError(
                provider=self._PROVIDER, status_code=None
            ) from exception

        if ceis_id is not None:
            data: dict[str, object] = raw
            graph = map_graph(payload=Payload(provider=self._PROVIDER, data=data))
        else:
            records: list[dict[str, object]] = raw

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
            entity=graph,
            fetched_at=fetched_at,
            merged_at=None,
            provider=self._PROVIDER,
        )
