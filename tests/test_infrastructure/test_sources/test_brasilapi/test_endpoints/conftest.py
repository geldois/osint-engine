from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from osint_engine.infrastructure.sources.brasilapi.endpoints.cep_v2_fetcher import (
    BrasilAPICEPv2Fetcher,
)
from osint_engine.infrastructure.sources.brasilapi.endpoints.cnpj_v1_fetcher import (
    BrasilAPICNPJv1Fetcher,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload
    from tests.test_infrastructure.test_sources.conftest import MakePayload

type MakeBrasilAPICNPJv1Fetcher = Callable[..., BrasilAPICNPJv1Fetcher]
type MakeBrasilAPICEPv2Fetcher = Callable[..., BrasilAPICEPv2Fetcher]


@pytest.fixture
def make_brasilapi_cnpj_fetcher() -> MakeBrasilAPICNPJv1Fetcher:
    """
    *,
    handler: Callable[[Request], Response]
    """

    def brasil_cnpj_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> BrasilAPICNPJv1Fetcher:
        return BrasilAPICNPJv1Fetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return brasil_cnpj_fetcher


@pytest.fixture
def brasilapi_cnpj_v1_valid_path() -> Path:
    """The path to the canonical valid BrasilAPI CNPJ v1 response file."""

    return Path(__file__).parent / "responses" / "brasilapi_cnpj_v1.json"


@pytest.fixture
def brasilapi_cnpj_v1_valid_payload(
    make_payload: MakePayload, brasilapi_cnpj_v1_valid_path: Path
) -> Payload:
    """The canonical valid BrasilAPI CNPJ v1 payload."""

    return make_payload(source="brasilapi", data=brasilapi_cnpj_v1_valid_path)


@pytest.fixture
def make_brasilapi_cep_fetcher() -> MakeBrasilAPICEPv2Fetcher:
    """
    *,
    handler: Callable[[Request], Response]
    """

    def brasil_cep_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> BrasilAPICEPv2Fetcher:
        return BrasilAPICEPv2Fetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return brasil_cep_fetcher


@pytest.fixture
def brasilapi_cep_v2_valid_path() -> Path:
    """The path to the canonical valid BrasilAPI CEP v2 response file."""

    return Path(__file__).parent / "responses" / "brasilapi_cep_v2.json"


@pytest.fixture
def brasilapi_cep_v2_valid_payload(
    make_payload: MakePayload, brasilapi_cep_v2_valid_path: Path
) -> Payload:
    """The canonical valid BrasilAPI CEP v2 payload."""

    return make_payload(source="brasilapi", data=brasilapi_cep_v2_valid_path)
