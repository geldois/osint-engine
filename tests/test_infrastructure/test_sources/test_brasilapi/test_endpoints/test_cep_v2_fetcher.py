from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING

import pytest
from httpx2 import Request, RequestError, Response

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.infrastructure.errors.data_source_error import DataSourceRequestError
from tests.data.brasilapi import CEP, CEP_DATA, NUMBER

if TYPE_CHECKING:
    from tests.test_infrastructure.test_sources.test_brasilapi.test_endpoints.conftest import (  # noqa: E501
        MakeBrasilAPICEPv2Fetcher,
    )


class TestBrasilAPICEPv2FetcherOnHTTPStatusError:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [400, 404, 429, 500, 503])
    async def test_wraps_error_preserving_status_code(
        self, make_brasilapi_cep_fetcher: MakeBrasilAPICEPv2Fetcher, status_code: int
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code)

        fetcher = make_brasilapi_cep_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(cep=CEP, number=NUMBER)

        assert exception.value.status_code == status_code

        assert exception.value.source == "brasilapi"


class TestBrasilAPICEPv2FetcherOnNetworkFailure:
    @pytest.mark.asyncio
    async def test_wraps_request_error_without_status_code(
        self, make_brasilapi_cep_fetcher: MakeBrasilAPICEPv2Fetcher
    ) -> None:
        def handler(request: Request) -> Response:
            message = "connection refused"

            raise RequestError(message=message, request=request)

        fetcher = make_brasilapi_cep_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(cep=CEP, number=NUMBER)

        assert exception.value.status_code is None

        assert exception.value.source == "brasilapi"


class TestBrasilAPICEPv2FetcherOnMalformedJSON:
    @pytest.mark.asyncio
    async def test_wraps_decode_error_without_status_code(
        self, make_brasilapi_cep_fetcher: MakeBrasilAPICEPv2Fetcher
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(status_code=200, content=b"not valid json {{{")

        fetcher = make_brasilapi_cep_fetcher(handler=handler)

        with pytest.raises(DataSourceRequestError) as exception:
            await fetcher.fetch(cep=CEP, number=NUMBER)

        assert exception.value.status_code is None

        assert exception.value.source == "brasilapi"


class TestBrasilAPICEPv2FetcherOnSuccess:
    @pytest.mark.asyncio
    async def test_returns_an_address_revision_stamped_at_the_fetch_boundary(
        self, make_brasilapi_cep_fetcher: MakeBrasilAPICEPv2Fetcher
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=CEP_DATA)

        fetcher = make_brasilapi_cep_fetcher(handler=handler)

        result = await fetcher.fetch(cep=CEP, number=NUMBER)

        assert isinstance(result.entity, Address)

        assert result.entity.number == NUMBER

        assert result.fetched_at.tzinfo is UTC

        assert result.merged_at is None
