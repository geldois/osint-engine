from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

import pytest
from httpx2 import Request, RequestError, Response

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.errors.data_source_error import DataSourceRequestError
from osint_engine.infrastructure.errors.external_credential_error import (
    ExternalCredentialRejectedError,
)

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from tests.test_infrastructure.test_sources.test_portal_transparencia.test_endpoints.conftest import (  # noqa: E501
        MakePortalTransparenciaCPFFetcher,
    )


_PF_RESPONSE_DATA: dict[str, object] = {
    "cpf": "128.734.***-**",
    "nome": "TARCIANA PAULA GOMES MEDEIROS",
    "sancionadoCEIS": False,
    "sancionadoCNEP": False,
    "servidor": True,
}


class TestPortalTransparenciaCPFFetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.status_code == status_code

        assert exception.value.source == "portal_transparencia"


class TestPortalTransparenciaCPFFetcherOnCredentialRejection:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [401, 403])
    async def test_raises_external_credential_rejected_error(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        with pytest.raises(ExternalCredentialRejectedError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.username == portal_transparencia_credential.username


class TestPortalTransparenciaCPFFetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:
            message = "connection refused"

            raise RequestError(message=message, request=request)

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.status_code is None

        assert exception.value.source == "portal_transparencia"


class TestPortalTransparenciaCPFFetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.status_code is None

        assert exception.value.source == "portal_transparencia"


class TestPortalTransparenciaCPFFetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_a_graph_revision_stamped_at_the_fetch_boundary(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=_PF_RESPONSE_DATA)

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert isinstance(result.entity, Graph)

        assert result.fetched_at.tzinfo is UTC

        assert result.merged_at is None

    @pytest.mark.asyncio
    async def test_sends_the_credential_api_key_as_a_request_header(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["chave-api-dados"] = request.headers["chave-api-dados"]

            return Response(200, json=_PF_RESPONSE_DATA)

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert captured["chave-api-dados"] == portal_transparencia_credential.api_key

    @pytest.mark.asyncio
    async def test_sends_the_cpf_as_a_query_parameter(
        self,
        make_portal_transparencia_cpf_fetcher: MakePortalTransparenciaCPFFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["path"] = str(request.url)

            return Response(200, json=_PF_RESPONSE_DATA)

        fetcher = make_portal_transparencia_cpf_fetcher(handler=handler)

        await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert captured["path"].startswith(
            "https://api.portaldatransparencia.gov.br/api-de-dados/pf?"
        )
        assert "cpf=10000000000" in captured["path"]
