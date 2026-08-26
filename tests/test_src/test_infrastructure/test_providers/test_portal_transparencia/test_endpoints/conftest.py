from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.ceaf_fetcher import (  # noqa: E501
    PortalTransparenciaCEAFFetcher,
)
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.ceis_fetcher import (  # noqa: E501
    PortalTransparenciaCEISFetcher,
)
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.cepim_fetcher import (  # noqa: E501
    PortalTransparenciaCEPIMFetcher,
)
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.cnep_fetcher import (  # noqa: E501
    PortalTransparenciaCNEPFetcher,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.providers.payload import Payload
    from tests.test_src.test_infrastructure.test_providers.conftest import MakePayload

type MakePortalTransparenciaCEAFFetcher = Callable[..., PortalTransparenciaCEAFFetcher]
type MakePortalTransparenciaCEISFetcher = Callable[..., PortalTransparenciaCEISFetcher]
type MakePortalTransparenciaCEPIMFetcher = Callable[
    ..., PortalTransparenciaCEPIMFetcher
]
type MakePortalTransparenciaCNEPFetcher = Callable[..., PortalTransparenciaCNEPFetcher]


@pytest.fixture
def portal_transparencia_credential() -> ExternalCredential:
    return ExternalCredential(
        api_key="test-api-key",
        provider=Provider.PORTAL_TRANSPARENCIA,
        username="analyst",
    )


@pytest.fixture
def make_portal_transparencia_ceis_fetcher() -> MakePortalTransparenciaCEISFetcher:

    def ceis_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaCEISFetcher:
        return PortalTransparenciaCEISFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return ceis_fetcher


@pytest.fixture
def make_portal_transparencia_cnep_fetcher() -> MakePortalTransparenciaCNEPFetcher:

    def cnep_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaCNEPFetcher:
        return PortalTransparenciaCNEPFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return cnep_fetcher


@pytest.fixture
def make_portal_transparencia_cepim_fetcher() -> MakePortalTransparenciaCEPIMFetcher:

    def cepim_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaCEPIMFetcher:
        return PortalTransparenciaCEPIMFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return cepim_fetcher


@pytest.fixture
def make_portal_transparencia_ceaf_fetcher() -> MakePortalTransparenciaCEAFFetcher:

    def ceaf_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaCEAFFetcher:
        return PortalTransparenciaCEAFFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return ceaf_fetcher


@pytest.fixture
def portal_transparencia_cnep_valid_path() -> Path:

    return Path(__file__).parent / "responses" / "portal_transparencia_cnep.json"


@pytest.fixture
def portal_transparencia_cnep_valid_payload(
    make_payload: MakePayload, portal_transparencia_cnep_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_cnep_valid_path
    )


@pytest.fixture
def portal_transparencia_ceis_valid_path() -> Path:

    return Path(__file__).parent / "responses" / "portal_transparencia_ceis.json"


@pytest.fixture
def portal_transparencia_ceis_valid_payload(
    make_payload: MakePayload, portal_transparencia_ceis_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_ceis_valid_path
    )
