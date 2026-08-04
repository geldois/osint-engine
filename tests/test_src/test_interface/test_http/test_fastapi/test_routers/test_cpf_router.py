from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.application.use_cases.expansion.expand_by_cpf import ExpandByCPF
from osint_engine.infrastructure.sources.portal_transparencia.endpoints.cpf_fetcher import (  # noqa: E501
    PortalTransparenciaCPFFetcher,
)
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app
from osint_engine.interface.http.schemas.graph_schema import GraphSchema

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from osint_engine.config.container import Container
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.conftest import MakeMemStorage
    from tests.test_src.test_interface.test_http.test_fastapi.conftest import (
        MakeContainer,
    )

_PF_RESPONSE_DATA: dict[str, object] = {
    "cpf": "100.000.000-00",
    "nome": "FULANO DE TAL",
    "sancionadoCEIS": False,
    "sancionadoCNEP": False,
}

CPF = "10000000000"


@pytest_asyncio.fixture
async def portal_transparencia_http_client() -> AsyncGenerator[AsyncClient, None]:

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, json=_PF_RESPONSE_DATA)

    async with AsyncClient(transport=MockTransport(handler)) as http_client:
        yield http_client


@pytest.fixture
def cpf_container(
    make_container: MakeContainer,
    make_mem_storage: MakeMemStorage,
    portal_transparencia_http_client: AsyncClient,
) -> Container:
    return make_container(
        http_client=portal_transparencia_http_client,
        mem_storage=make_mem_storage(),
    )


@pytest_asyncio.fixture
async def client(cpf_container: Container) -> AsyncGenerator[AsyncClient, None]:
    credential = ExternalCredential(
        api_key="test-api-key",
        provider=Provider.PORTAL_TRANSPARENCIA,
        username="admin",
    )

    async with cpf_container.uow_factory() as uow:
        await uow.external_credentials.save(credential=credential)

    app = build_fastapi_app(container=cpf_container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role="admin")


class TestGetCPFAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get(f"/cpf/{CPF}")

        assert response.status_code == 401


class TestGetCPFExpansion:
    @pytest.mark.asyncio
    async def test_valid_token_and_known_credential_returns_graph_schema(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/cpf/{CPF}", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 200
        GraphSchema.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_returns_422_for_a_malformed_cpf(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            "/cpf/123", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_404_when_no_credential_is_configured(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        portal_transparencia_http_client: AsyncClient,
        valid_token: str,
    ) -> None:
        container = make_container(
            http_client=portal_transparencia_http_client,
            mem_storage=make_mem_storage(),
        )
        app = build_fastapi_app(container=container)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/cpf/{CPF}", headers={"Authorization": f"Bearer {valid_token}"}
            )

        assert response.status_code == 404


class TestCPFCompositionRoot:
    def test_container_resolves_cpf_fetcher_and_use_case(
        self, cpf_container: Container
    ) -> None:
        assert isinstance(
            cpf_container.fetchers.cpf_fetcher, PortalTransparenciaCPFFetcher
        )

        use_case = cpf_container.use_cases.expand_by_cpf(cpf=CPF, username="admin")

        assert isinstance(use_case, ExpandByCPF)
