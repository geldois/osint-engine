from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

import pytest
from httpx2 import Request, RequestError, Response

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.errors.external_credential_error import (
    ExternalCredentialRejectedError,
)
from osint_engine.infrastructure.errors.provider_error import (
    InsufficientCreditsError,
    ProviderRequestError,
    UnexpectedPayloadError,
)

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import ExternalCredential
    from tests.test_src.test_infrastructure.test_providers.test_kipflow.test_endpoints.conftest import (  # noqa: E501
        MakeKipFlowLegalProcessFetcher,
    )

_TEST_CPF = "52998224563"
_TEST_CNPJ = "35965725000107"

_LEGAL_PROCESS_RECORD_DATA: dict[str, object] = {
    "numeroProcessoUnico": "0001234-56.2024.8.26.0100",
    "urlProcesso": "https://kipflow.io/processos/0001234",
    "tribunal": "TJSP",
    "uf": "SP",
    "classeProcessual": {"nome": "Execução de Título Extrajudicial"},
    "dataDistribuicao": "2024-03-10",
    "valorCausa": {"valor": 150000.50, "moeda": "BRL"},
    "eSegredoJustica": False,
    "statusPredictus": {"statusProcesso": "Em andamento", "valorExecucao": 150000.50},
}

_SUCCESS_RESPONSE_DATA: dict[str, object] = {
    "success": True,
    "data": [_LEGAL_PROCESS_RECORD_DATA],
    "cost": 3.50,
    "costFormatted": "R$ 3,50",
}


class TestKipFlowLegalProcessFetcherOnRequest:
    @pytest.mark.asyncio
    async def test_sends_cpf_path_and_api_key_header_for_an_11_digit_document(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["url"] = str(request.url)
            captured["api_key"] = request.headers["X-API-Key"]

            return Response(200, json=_SUCCESS_RESPONSE_DATA)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)

        assert captured["url"].startswith(
            "https://api.kipflow.io/legal/v1/parties/cpf?"
        )
        assert f"q={_TEST_CPF}" in captured["url"]
        assert captured["api_key"] == kipflow_credential.api_key

    @pytest.mark.asyncio
    async def test_sends_cnpj_path_for_a_14_digit_document(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["url"] = str(request.url)

            return Response(200, json=_SUCCESS_RESPONSE_DATA)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        await fetcher.fetch(cpf_or_cnpj=_TEST_CNPJ, credential=kipflow_credential)

        assert captured["url"].startswith(
            "https://api.kipflow.io/legal/v1/parties/cnpj?"
        )
        assert f"q={_TEST_CNPJ}" in captured["url"]


class TestKipFlowLegalProcessFetcherOnCredentialRejection:
    @pytest.mark.asyncio
    async def test_raises_external_credential_rejected_error(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(401)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        with pytest.raises(ExternalCredentialRejectedError) as exception:
            await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.username == kipflow_credential.username


class TestKipFlowLegalProcessFetcherOnInsufficientCredits:
    @pytest.mark.asyncio
    async def test_raises_insufficient_credits_error(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(402)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        with pytest.raises(InsufficientCreditsError) as exception:
            await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.provider == "kipflow"


class TestKipFlowLegalProcessFetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.status_code == status_code
        assert exception.value.provider == "kipflow"


class TestKipFlowLegalProcessFetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:
            raise RequestError(message="connection refused", request=request)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.status_code is None
        assert exception.value.provider == "kipflow"


class TestKipFlowLegalProcessFetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.status_code is None
        assert exception.value.provider == "kipflow"


class TestKipFlowLegalProcessFetcherOnUnsuccessfulPayload:
    @pytest.mark.asyncio
    async def test_raises_unexpected_payload_error_when_success_is_false(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json={"success": False})

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        with pytest.raises(UnexpectedPayloadError):
            await fetcher.fetch(cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential)


class TestKipFlowLegalProcessFetcherOnEmptyResult:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_processes_are_found(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json={"success": True, "data": []})

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential
        )

        assert result is None


class TestKipFlowLegalProcessFetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_a_graph_revision_stamped_at_the_fetch_boundary(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_legal_process_fetcher: MakeKipFlowLegalProcessFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=_SUCCESS_RESPONSE_DATA)

        fetcher = make_kipflow_legal_process_fetcher(handler=handler)

        result = await fetcher.fetch(
            cpf_or_cnpj=_TEST_CPF, credential=kipflow_credential
        )

        assert result is not None
        assert isinstance(result.entity, Graph)
        assert result.fetched_at.tzinfo is UTC
        assert result.merged_at is None
        assert result.provider == "kipflow"
