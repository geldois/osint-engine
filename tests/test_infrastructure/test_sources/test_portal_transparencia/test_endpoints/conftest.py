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
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.ceis_fetcher import (  # noqa: E501
    PortalTransparenciaCEISFetcher,
)
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cnep_fetcher import (  # noqa: E501
    PortalTransparenciaCNEPFetcher,
)

if TYPE_CHECKING:
    from osint_engine.infrastructure.sources.payload import Payload
    from tests.test_infrastructure.test_sources.conftest import MakePayload

type MakePortalTransparenciaCEISFetcher = Callable[..., PortalTransparenciaCEISFetcher]
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
    """
    *,
    handler: Callable[[Request], Response]
    """

    def ceis_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaCEISFetcher:
        return PortalTransparenciaCEISFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return ceis_fetcher


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


@pytest.fixture
def portal_transparencia_cnep_valid_path() -> Path:
    """The path to the canonical valid Portal da Transparência CNEP response file."""

    return Path(__file__).parent / "responses" / "portal_transparencia_cnep.json"


@pytest.fixture
def portal_transparencia_cnep_valid_payload(
    make_payload: MakePayload, portal_transparencia_cnep_valid_path: Path
) -> Payload:
    """The canonical valid Portal da Transparência CNEP payload."""

    return make_payload(
        source="portal_transparencia", data=portal_transparencia_cnep_valid_path
    )


@pytest.fixture
def portal_transparencia_ceis_valid_path() -> Path:
    """The path to the canonical valid Portal da Transparência CEIS response file."""

    return Path(__file__).parent / "responses" / "portal_transparencia_ceis.json"


@pytest.fixture
def portal_transparencia_ceis_valid_payload(
    make_payload: MakePayload, portal_transparencia_ceis_valid_path: Path
) -> Payload:
    """The canonical valid Portal da Transparência CEIS payload."""

    return make_payload(
        source="portal_transparencia", data=portal_transparencia_ceis_valid_path
    )
