from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from osint_engine.infrastructure.sources.brasilapi.brasilapi_fetcher import (
    BrasilAPICNPJFetcher,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload
    from tests.conftest import MakePayload

type MakeBrasilAPICNPJFetcher = Callable[..., BrasilAPICNPJFetcher]


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
    """ """

    return Path(__file__).parent / "responses" / "brasilapi_cnpj_v1_valid.json"


@pytest.fixture
def brasilapi_cnpj_v1_valid_payload(
    make_payload: MakePayload, brasilapi_cnpj_v1_valid_path: Path
) -> Payload:
    """ """

    return make_payload(source="brasilapi", data=brasilapi_cnpj_v1_valid_path)
