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
        MakePortalTransparenciaCNEPFetcher,
    )

# TEST DOUBLES


_CNEP_RECORD_DATA = {
    "dataFimSancao": "2026-01-01",
    "dataInicioSancao": "2024-01-01",
    "dataPublicacaoSancao": "2024-01-15",
    "fundamentacao": [{"codigo": "1", "descricao": "Lei 8.666/1993, art. 87"}],
    "linkPublicacao": "https://portaldatransparencia.gov.br/sancoes/cnep/123",
    "numeroProcesso": "123/2024",
    "orgaoSancionador": {"nome": "CGU"},
    "pessoa": {
        "cnpjFormatado": "33.754.482/0001-24",
        "nomeFantasiaReceita": "EMPRESA FANTASIA",
        "razaoSocialReceita": "EMPRESA LTDA",
    },
    "tipoSancao": {"descricaoResumida": "Suspensão"},
    "valorMulta": "1.000,50",
}

_CNEP_RESPONSE_DATA = [_CNEP_RECORD_DATA]


# TESTS


class TestPortalTransparenciaCNEPFetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(
                cpf_or_cnpj="33754482000124",
                cnep_id=None,
                credential=portal_transparencia_credential,
            )

        assert exception.value.status_code == status_code

        assert exception.value.source == "portal_transparencia"


class TestPortalTransparenciaCNEPFetcherOnCredentialRejection:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [401, 403])
    async def test_raises_external_credential_rejected_error(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        with pytest.raises(ExternalCredentialRejectedError) as exception:
            await fetcher.fetch(
                cpf_or_cnpj="33754482000124",
                cnep_id=None,
                credential=portal_transparencia_credential,
            )

        assert exception.value.username == portal_transparencia_credential.username


class TestPortalTransparenciaCNEPFetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:
            message = "connection refused"

            raise RequestError(message=message, request=request)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(
                cpf_or_cnpj="33754482000124",
                cnep_id=None,
                credential=portal_transparencia_credential,
            )

        assert exception.value.status_code is None

        assert exception.value.source == "portal_transparencia"


class TestPortalTransparenciaCNEPFetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(
                cpf_or_cnpj="33754482000124",
                cnep_id=None,
                credential=portal_transparencia_credential,
            )

        assert exception.value.status_code is None

        assert exception.value.source == "portal_transparencia"


class TestPortalTransparenciaCNEPFetcherOnEmptyResult:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_sanctions_are_found(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=[])

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf_or_cnpj="33754482000124",
            cnep_id=None,
            credential=portal_transparencia_credential,
        )

        assert result is None


class TestPortalTransparenciaCNEPFetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_a_graph_revision_stamped_at_the_fetch_boundary(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=_CNEP_RESPONSE_DATA)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf_or_cnpj="33754482000124",
            cnep_id=None,
            credential=portal_transparencia_credential,
        )

        assert result is not None
        assert isinstance(result.entity, Graph)

        assert result.fetched_at.tzinfo is UTC

        assert result.merged_at is None

    @pytest.mark.asyncio
    async def test_sends_the_credential_api_key_as_a_request_header(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["chave-api-dados"] = request.headers["chave-api-dados"]

            return Response(200, json=_CNEP_RESPONSE_DATA)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        await fetcher.fetch(
            cpf_or_cnpj="33754482000124",
            cnep_id=None,
            credential=portal_transparencia_credential,
        )

        assert captured["chave-api-dados"] == portal_transparencia_credential.api_key

    @pytest.mark.asyncio
    async def test_filters_by_codigo_sancionado_when_cnep_id_is_absent(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["path"] = str(request.url)

            return Response(200, json=_CNEP_RESPONSE_DATA)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        await fetcher.fetch(
            cpf_or_cnpj="33754482000124",
            cnep_id=None,
            credential=portal_transparencia_credential,
        )

        assert captured["path"].startswith(
            "https://api.portaldatransparencia.gov.br/api-de-dados/cnep?"
        )
        assert "codigoSancionado=33754482000124" in captured["path"]
        assert "pagina=1" in captured["path"]

    @pytest.mark.asyncio
    async def test_requests_the_single_record_by_id_when_cnep_id_is_provided(
        self,
        make_portal_transparencia_cnep_fetcher: MakePortalTransparenciaCNEPFetcher,
        portal_transparencia_credential: ExternalCredential,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["path"] = str(request.url)

            return Response(200, json=_CNEP_RECORD_DATA)

        fetcher = make_portal_transparencia_cnep_fetcher(handler=handler)

        await fetcher.fetch(
            cpf_or_cnpj="33754482000124",
            cnep_id=42,
            credential=portal_transparencia_credential,
        )

        assert captured["path"].endswith("cnep/42")
