from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx2 import Request, RequestError, Response

from osint_engine.domain.entities.bases.graph import Graph
from osint_engine.infrastructure.errors.data_source_error import DataSourceRequestError
from tests.test_infrastructure.test_sources._data import CNPJ, COMPLETE_PAYLOAD_DATA

if TYPE_CHECKING:
    from tests.test_infrastructure.test_sources.test_brasilapi.conftest import (
        MakeBrasilAPICNPJFetcher,
    )


class TestBrasilAPICNPJFetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self, make_brasilapi_cnpj_fetcher: MakeBrasilAPICNPJFetcher, status_code: int
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_brasilapi_cnpj_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(CNPJ)

        assert exception.value.status_code == status_code

        assert exception.value.source == "brasilapi"


class TestBrasilAPICNPJFetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self, make_brasilapi_cnpj_fetcher: MakeBrasilAPICNPJFetcher
    ) -> None:
        def handler(request: Request) -> Response:
            message = "connection refused"

            raise RequestError(message=message, request=request)

        fetcher = make_brasilapi_cnpj_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(CNPJ)

        assert exception.value.status_code is None

        assert exception.value.source == "brasilapi"


class TestBrasilAPICNPJFetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self, make_brasilapi_cnpj_fetcher: MakeBrasilAPICNPJFetcher
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_brasilapi_cnpj_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(CNPJ)

        assert exception.value.status_code is None

        assert exception.value.source == "brasilapi"


class TestBrasilAPICNPJFetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_graph(
        self, make_brasilapi_cnpj_fetcher: MakeBrasilAPICNPJFetcher
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=COMPLETE_PAYLOAD_DATA)

        fetcher = make_brasilapi_cnpj_fetcher(handler=handler)

        result = await fetcher.fetch(CNPJ)

        assert isinstance(result, Graph)
