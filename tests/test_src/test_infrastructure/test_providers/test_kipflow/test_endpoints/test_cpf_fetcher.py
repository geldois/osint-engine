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
        MakeKipFlowCPFFetcher,
    )

_TEST_CPF = "52998224563"

_SUCCESS_RESPONSE_DATA: dict[str, object] = {
    "success": True,
    "data": {
        "cpf": _TEST_CPF,
        "nome": "FULANO DE TAL",
        "nasc": "1990-01-01",
        "situacao_cadastral": "REGULAR",
        "data_inscricao": "2010-05-20",
    },
}


class TestKipFlowCPFFetcherOnRequest:
    @pytest.mark.asyncio
    async def test_sends_the_expected_url_datasets_and_api_key_header(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: Request) -> Response:
            captured["url"] = str(request.url)
            captured["api_key"] = request.headers["X-API-Key"]

            return Response(200, json=_SUCCESS_RESPONSE_DATA)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert captured["url"].startswith("https://api.kipflow.io/people/v1/search?")
        assert f"cpf={_TEST_CPF}" in captured["url"]
        assert "datasets=basic%2Cregistration_status" in captured["url"]
        assert captured["api_key"] == kipflow_credential.api_key


class TestKipFlowCPFFetcherOnNotFound:
    @pytest.mark.asyncio
    async def test_returns_none_without_raising(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(404)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        result = await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert result is None


class TestKipFlowCPFFetcherOnCredentialRejection:
    @pytest.mark.asyncio
    async def test_raises_external_credential_rejected_error(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(401)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        with pytest.raises(ExternalCredentialRejectedError) as exception:
            await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.username == kipflow_credential.username


class TestKipFlowCPFFetcherOnInsufficientCredits:
    @pytest.mark.asyncio
    async def test_raises_insufficient_credits_error(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(402)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        with pytest.raises(InsufficientCreditsError) as exception:
            await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.provider == "kipflow"


class TestKipFlowCPFFetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
        status_code: int,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.status_code == status_code
        assert exception.value.provider == "kipflow"


class TestKipFlowCPFFetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:
            message = "connection refused"

            raise RequestError(message=message, request=request)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.status_code is None
        assert exception.value.provider == "kipflow"


class TestKipFlowCPFFetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        with pytest.raises(ProviderRequestError) as exception:
            await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert exception.value.status_code is None
        assert exception.value.provider == "kipflow"


class TestKipFlowCPFFetcherOnUnsuccessfulPayload:
    @pytest.mark.asyncio
    async def test_raises_unexpected_payload_error_when_success_is_false(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json={"success": False})

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        with pytest.raises(UnexpectedPayloadError):
            await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)


class TestKipFlowCPFFetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_a_graph_revision_stamped_at_the_fetch_boundary(
        self,
        kipflow_credential: ExternalCredential,
        make_kipflow_cpf_fetcher: MakeKipFlowCPFFetcher,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=_SUCCESS_RESPONSE_DATA)

        fetcher = make_kipflow_cpf_fetcher(handler=handler)

        result = await fetcher.fetch(cpf=_TEST_CPF, credential=kipflow_credential)

        assert result is not None
        assert isinstance(result.entity, Graph)
        assert result.fetched_at.tzinfo is UTC
        assert result.merged_at is None
        assert result.provider == "kipflow"
