from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from osint_engine.infrastructure.sources.brasilapi.brasilapi_fetcher import (
    BrasilAPICNPJFetcher,
)
from osint_engine.infrastructure.sources.payload import Payload

type MakeBrasilAPICNPJFetcher = Callable[..., BrasilAPICNPJFetcher]
type MakePayload = Callable[..., Payload]


@pytest.fixture
def make_payload() -> MakePayload:
    """
    *,
    source: str,
    data: dict[str, object] | Path
    """

    def payload(*, source: str, data: dict[str, object] | Path) -> Payload:
        if isinstance(data, Path):
            with Path.open(data) as file:
                data_: dict[str, object] = json.load(file)

                return Payload(source=source, data=data_)

        return Payload(source=source, data=data)

    return payload


@pytest.fixture
def make_brasilapi_cnpj_fetcher() -> MakeBrasilAPICNPJFetcher:
    """
    *,
    handler: Callable[[Request], Response]
    """

    def brasil_cnpj_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> BrasilAPICNPJFetcher:
        return BrasilAPICNPJFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return brasil_cnpj_fetcher


@pytest.fixture
def brasilapi_cnpj_v1_valid_path() -> Path:
    """The path to the canonical valid BrasilAPI CNPJ v1 response file."""

    return Path(__file__).parent / "responses" / "brasilapi_cnpj_v1_valid.json"


@pytest.fixture
def brasilapi_cnpj_v1_valid_payload(
    make_payload: MakePayload, brasilapi_cnpj_v1_valid_path: Path
) -> Payload:
    """The canonical valid BrasilAPI CNPJ v1 payload."""

    return make_payload(source="brasilapi", data=brasilapi_cnpj_v1_valid_path)
