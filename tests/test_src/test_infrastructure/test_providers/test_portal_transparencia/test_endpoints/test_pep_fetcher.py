from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

import pytest
from httpx2 import Request, RequestError, Response

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.errors.external_credential_error import (
    ExternalCredentialRejectedError,
)
from osint_engine.infrastructure.errors.provider_error import ProviderRequestError

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from tests.test_src.test_infrastructure.test_providers.test_portal_transparencia.test_endpoints.conftest import (  # noqa: E501
        MakePortalTransparenciaPEPFetcher,
    )

_PEP_RECORD_DATA = {
    "cpf": "100.000.000-00",
    "nome": "FULANO DE TAL",
    "sigla_funcao": "MIN",
    "descricao_funcao": "MINISTRO DE ESTADO",
    "nivel_funcao": "1",
    "cod_orgao": "26000",
    "nome_orgao": "MINISTERIO DA FAZENDA",
    "dt_inicio_exercicio": "2023-01-01",
    "dt_fim_exercicio": None,
    "dt_fim_carencia": None,
}

_PEP_RESPONSE_DATA = [_PEP_RECORD_DATA]


class TestPortalTransparenciaPEPFetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.status_code == status_code
        assert exception.value.provider == "portal_transparencia"


class TestPortalTransparenciaPEPFetcherOnCredentialRejection:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [401, 403])
    async def test_raises_external_credential_rejected_error(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        with pytest.raises(ExternalCredentialRejectedError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.username == portal_transparencia_credential.username


class TestPortalTransparenciaPEPFetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:
            raise RequestError(message="connection refused", request=request)

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.status_code is None
        assert exception.value.provider == "portal_transparencia"


class TestPortalTransparenciaPEPFetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(
                cpf="10000000000", credential=portal_transparencia_credential
            )

        assert exception.value.status_code is None
        assert exception.value.provider == "portal_transparencia"


class TestPortalTransparenciaPEPFetcherOnEmptyResult:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_records_are_found(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=[])

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert result is None


class TestPortalTransparenciaPEPFetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_a_graph_revision_stamped_at_the_fetch_boundary(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=_PEP_RESPONSE_DATA)

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert result is not None
        assert isinstance(result.entity, Graph)
        assert result.fetched_at.tzinfo is UTC
        assert result.merged_at is None

    @pytest.mark.asyncio
    async def test_sends_the_credential_api_key_as_a_request_header(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["chave-api-dados"] = request.headers["chave-api-dados"]

            return Response(200, json=_PEP_RESPONSE_DATA)

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert captured["chave-api-dados"] == portal_transparencia_credential.api_key

    @pytest.mark.asyncio
    async def test_filters_by_cpf(
        self,
        make_portal_transparencia_pep_fetcher: MakePortalTransparenciaPEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["path"] = str(request.url)

            return Response(200, json=_PEP_RESPONSE_DATA)

        fetcher = make_portal_transparencia_pep_fetcher(handler=handler)

        await fetcher.fetch(
            cpf="10000000000", credential=portal_transparencia_credential
        )

        assert captured["path"].startswith(
            "https://api.portaldatransparencia.gov.br/api-de-dados/peps?"
        )
        assert "cpf=10000000000" in captured["path"]
        assert "pagina=1" in captured["path"]
