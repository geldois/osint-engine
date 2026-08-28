from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from httpx2 import AsyncClient, MockTransport

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.providers.kipflow.endpoints.cpf_fetcher import (
    KipFlowCPFFetcher,
)
from osint_engine.infrastructure.providers.kipflow.endpoints.legal_process_fetcher import (  # noqa: E501
    KipFlowLegalProcessFetcher,
)
from osint_engine.infrastructure.providers.kipflow.in_memory_rate_limiter import (
    InMemoryKipFlowRateLimiter,
)

if TYPE_CHECKING:
    from httpx2 import Request, Response

type MakeKipFlowCPFFetcher = Callable[..., KipFlowCPFFetcher]
type MakeKipFlowLegalProcessFetcher = Callable[..., KipFlowLegalProcessFetcher]


@pytest.fixture
def kipflow_credential() -> ExternalCredential:
    return ExternalCredential(
        api_key="test-api-key", provider=Provider.KIPFLOW, username="analyst"
    )


@pytest.fixture
def make_kipflow_cpf_fetcher() -> MakeKipFlowCPFFetcher:

    def cpf_fetcher(*, handler: Callable[[Request], Response]) -> KipFlowCPFFetcher:
        return KipFlowCPFFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler)),
            rate_limiter=InMemoryKipFlowRateLimiter(),
        )

    return cpf_fetcher


@pytest.fixture
def make_kipflow_legal_process_fetcher() -> MakeKipFlowLegalProcessFetcher:

    def legal_process_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> KipFlowLegalProcessFetcher:
        return KipFlowLegalProcessFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler)),
            rate_limiter=InMemoryKipFlowRateLimiter(),
        )

    return legal_process_fetcher
