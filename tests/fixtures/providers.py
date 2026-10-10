from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from httpx2 import AsyncClient, MockTransport

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.providers.brasilapi.endpoints.cep_v2_fetcher import (
    BrasilAPICEPv2Fetcher,
)
from osint_engine.infrastructure.providers.brasilapi.endpoints.cnpj_v1_fetcher import (
    BrasilAPICNPJv1Fetcher,
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
from osint_engine.infrastructure.providers.payload import Payload
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
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.pep_fetcher import (  # noqa: E501
    PortalTransparenciaPEPFetcher,
)

if TYPE_CHECKING:
    from httpx2 import Request, Response

_PROVIDERS_DIR = (
    Path(__file__).parents[1] / "test_src" / "test_infrastructure" / "test_providers"
)

type MakeBrasilAPICEPv2Fetcher = Callable[..., BrasilAPICEPv2Fetcher]
type MakeBrasilAPICNPJv1Fetcher = Callable[..., BrasilAPICNPJv1Fetcher]
type MakeKipFlowCPFFetcher = Callable[..., KipFlowCPFFetcher]
type MakeKipFlowLegalProcessFetcher = Callable[..., KipFlowLegalProcessFetcher]
type MakePayload = Callable[..., Payload]
type MakePortalTransparenciaCEAFFetcher = Callable[..., PortalTransparenciaCEAFFetcher]
type MakePortalTransparenciaCEISFetcher = Callable[..., PortalTransparenciaCEISFetcher]
type MakePortalTransparenciaCEPIMFetcher = Callable[
    ..., PortalTransparenciaCEPIMFetcher
]
type MakePortalTransparenciaCNEPFetcher = Callable[..., PortalTransparenciaCNEPFetcher]
type MakePortalTransparenciaPEPFetcher = Callable[..., PortalTransparenciaPEPFetcher]


def _response_path(*, provider_directory: str, file_name: str) -> Path:
    return (
        _PROVIDERS_DIR / provider_directory / "test_endpoints" / "responses" / file_name
    )


@pytest.fixture
def make_payload() -> MakePayload:

    def payload(*, provider: str, data: dict[str, object] | Path) -> Payload:
        if isinstance(data, Path):
            with Path.open(data) as file:
                data_: dict[str, object] = json.load(file)

                return Payload(provider=provider, data=data_)

        return Payload(provider=provider, data=data)

    return payload


@pytest.fixture
def make_brasilapi_cnpj_fetcher() -> MakeBrasilAPICNPJv1Fetcher:

    def brasil_cnpj_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> BrasilAPICNPJv1Fetcher:
        return BrasilAPICNPJv1Fetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return brasil_cnpj_fetcher


@pytest.fixture
def brasilapi_cnpj_v1_valid_path() -> Path:

    return _response_path(
        provider_directory="test_brasilapi", file_name="brasilapi_cnpj_v1.json"
    )


@pytest.fixture
def brasilapi_cnpj_v1_valid_payload(
    make_payload: MakePayload, brasilapi_cnpj_v1_valid_path: Path
) -> Payload:

    return make_payload(provider="brasilapi", data=brasilapi_cnpj_v1_valid_path)


@pytest.fixture
def make_brasilapi_cep_fetcher() -> MakeBrasilAPICEPv2Fetcher:

    def brasil_cep_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> BrasilAPICEPv2Fetcher:
        return BrasilAPICEPv2Fetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return brasil_cep_fetcher


@pytest.fixture
def brasilapi_cep_v2_valid_path() -> Path:

    return _response_path(
        provider_directory="test_brasilapi", file_name="brasilapi_cep_v2.json"
    )


@pytest.fixture
def brasilapi_cep_v2_valid_payload(
    make_payload: MakePayload, brasilapi_cep_v2_valid_path: Path
) -> Payload:

    return make_payload(provider="brasilapi", data=brasilapi_cep_v2_valid_path)


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
def make_portal_transparencia_pep_fetcher() -> MakePortalTransparenciaPEPFetcher:

    def pep_fetcher(
        *, handler: Callable[[Request], Response]
    ) -> PortalTransparenciaPEPFetcher:
        return PortalTransparenciaPEPFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler))
        )

    return pep_fetcher


@pytest.fixture
def portal_transparencia_cnep_valid_path() -> Path:

    return _response_path(
        provider_directory="test_portal_transparencia",
        file_name="portal_transparencia_cnep.json",
    )


@pytest.fixture
def portal_transparencia_cnep_valid_payload(
    make_payload: MakePayload, portal_transparencia_cnep_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_cnep_valid_path
    )


@pytest.fixture
def portal_transparencia_ceis_valid_path() -> Path:

    return _response_path(
        provider_directory="test_portal_transparencia",
        file_name="portal_transparencia_ceis.json",
    )


@pytest.fixture
def portal_transparencia_ceis_valid_payload(
    make_payload: MakePayload, portal_transparencia_ceis_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_ceis_valid_path
    )


@pytest.fixture
def portal_transparencia_cepim_valid_path() -> Path:

    return _response_path(
        provider_directory="test_portal_transparencia",
        file_name="portal_transparencia_cepim.json",
    )


@pytest.fixture
def portal_transparencia_cepim_valid_payload(
    make_payload: MakePayload, portal_transparencia_cepim_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_cepim_valid_path
    )


@pytest.fixture
def portal_transparencia_ceaf_valid_path() -> Path:

    return _response_path(
        provider_directory="test_portal_transparencia",
        file_name="portal_transparencia_ceaf.json",
    )


@pytest.fixture
def portal_transparencia_ceaf_valid_payload(
    make_payload: MakePayload, portal_transparencia_ceaf_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_ceaf_valid_path
    )


@pytest.fixture
def portal_transparencia_pep_valid_path() -> Path:

    return _response_path(
        provider_directory="test_portal_transparencia",
        file_name="portal_transparencia_pep.json",
    )


@pytest.fixture
def portal_transparencia_pep_valid_payload(
    make_payload: MakePayload, portal_transparencia_pep_valid_path: Path
) -> Payload:

    return make_payload(
        provider="portal_transparencia", data=portal_transparencia_pep_valid_path
    )
