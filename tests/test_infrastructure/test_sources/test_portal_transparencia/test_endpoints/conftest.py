from __future__ import annotations

from collections.abc import Callable

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cnep_fetcher import (  # noqa: E501
    PortalTransparenciaCNEPFetcher,
)

type MakePortalTransparenciaCNEPFetcher = Callable[
    ..., PortalTransparenciaCNEPFetcher
]


@pytest.fixture
def portal_transparencia_credential() -> ExternalCredential:
    return ExternalCredential(
        api_key="test-api-key",
        provider=Provider.PORTAL_TRANSPARENCIA,
        username="analyst",
    )


@pytest.fixture
def make_portal_transparencia_cnep_fetcher() -> MakePortalTransparenciaCNEPFetcher:
    """
    *,
    handler: Callable[[Request], Response]
    """

    def cnep_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaCNEPFetcher:
        return PortalTransparenciaCNEPFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return cnep_fetcher
