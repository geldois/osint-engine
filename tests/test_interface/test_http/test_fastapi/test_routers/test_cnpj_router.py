from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.user import Role
from osint_engine.interface.http.fastapi.fastapi import build_fastapi_app
from tests.data.brasilapi import CNPJ, COMPLETE_PAYLOAD_DATA

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.test_interface.test_http.test_fastapi.conftest import MakeContainer


@pytest_asyncio.fixture(loop_scope="session")
async def brasilapi_http_client() -> AsyncGenerator[AsyncClient, None]:
    """An HTTP client whose transport serves a valid BrasilAPI CNPJ payload."""

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, json=COMPLETE_PAYLOAD_DATA)

    async with AsyncClient(transport=MockTransport(handler)) as http_client:
        yield http_client


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    make_container: MakeContainer, brasilapi_http_client: AsyncClient
) -> AsyncGenerator[AsyncClient, None]:
    container = make_container(http_client=brasilapi_http_client)
    app = build_fastapi_app(container=container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role=Role.ADMIN)


@pytest.fixture
def viewer_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="visitor", role=Role.VIEWER)


# TESTS


class TestGetCnpjAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get(f"/cnpj/{CNPJ}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_token_includes_www_authenticate_bearer(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(f"/cnpj/{CNPJ}")

        assert response.headers.get("WWW-Authenticate") == "Bearer"

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get(
            f"/cnpj/{CNPJ}", headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401


class TestCnpjRouterScope:
    @pytest.mark.asyncio
    async def test_unrelated_path_is_not_routed_to_cnpj_handler(
        self, client: AsyncClient
    ) -> None:
        """The router is mounted under /cnpj; without that prefix a
        `{cnpj:path}` route would swallow every unrelated path."""

        response = await client.get("/some/unrelated/path")

        assert response.status_code == 404


class TestGetCnpjExpansion:
    @pytest.mark.asyncio
    async def test_valid_token_returns_200(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/cnpj/{CNPJ}", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_response_includes_correlation_id_header(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/cnpj/{CNPJ}", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert "x-correlation-id" in response.headers

    @pytest.mark.asyncio
    async def test_correlation_id_header_is_a_valid_uuid(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/cnpj/{CNPJ}", headers={"Authorization": f"Bearer {valid_token}"}
        )

        UUID(response.headers["x-correlation-id"])

    @pytest.mark.asyncio
    async def test_viewer_token_also_returns_200(
        self, client: AsyncClient, viewer_token: str
    ) -> None:
        response = await client.get(
            f"/cnpj/{CNPJ}", headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 200


class TestCnpjRateLimit:
    @pytest.mark.asyncio
    async def test_viewer_exceeding_limit_returns_429(
        self, client: AsyncClient, viewer_token: str
    ) -> None:
        headers = {"Authorization": f"Bearer {viewer_token}"}

        for _ in range(5):
            await client.get(f"/cnpj/{CNPJ}", headers=headers)

        response = await client.get(f"/cnpj/{CNPJ}", headers=headers)

        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_admin_bucket_is_isolated_from_viewer_bucket(
        self, client: AsyncClient, valid_token: str, viewer_token: str
    ) -> None:
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        admin_headers = {"Authorization": f"Bearer {valid_token}"}

        for _ in range(6):
            await client.get(f"/cnpj/{CNPJ}", headers=viewer_headers)

        response = await client.get(f"/cnpj/{CNPJ}", headers=admin_headers)

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_global_bucket_caps_traffic_regardless_of_role_limit(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        """ADMIN's own bucket allows 60/min, well past the 30/min combined
        ceiling that protects the shared upstream BrasilAPI quota — the
        global bucket must reject before ADMIN's role bucket would."""

        headers = {"Authorization": f"Bearer {valid_token}"}

        for _ in range(30):
            await client.get(f"/cnpj/{CNPJ}", headers=headers)

        response = await client.get(f"/cnpj/{CNPJ}", headers=headers)

        assert response.status_code == 429
