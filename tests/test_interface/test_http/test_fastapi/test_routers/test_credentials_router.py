from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient

from osint_engine.application.auth.external_credential import Provider
from osint_engine.interface.http.fastapi.fastapi import build_fastapi_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from osint_engine.infrastructure.persistence.mem.mem_storage import MemStorage
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.conftest import MakeMemStorage
    from tests.test_interface.test_http.test_fastapi.conftest import MakeContainer


@pytest.fixture
def mem_storage(make_mem_storage: MakeMemStorage) -> MemStorage:
    return make_mem_storage()


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    make_container: MakeContainer, mem_storage: MemStorage
) -> AsyncGenerator[AsyncClient, None]:
    container = make_container(mem_storage=mem_storage)
    app = build_fastapi_app(container=container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role="admin")


class TestPostCredentialAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
        )

        assert response.status_code == 401


class TestPostCredentialSubmission:
    @pytest.mark.asyncio
    async def test_valid_token_returns_204(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_saves_the_credential_for_the_authenticated_username(
        self, client: AsyncClient, valid_token: str, mem_storage: MemStorage
    ) -> None:
        await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        credential = mem_storage.external_credentials[
            ("admin", Provider.PORTAL_TRANSPARENCIA)
        ]

        assert credential.api_key == "test-api-key"
