from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient

from osint_engine.application.auth.external_credential import Provider
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from osint_engine.config.container import Container
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    container: Container,
) -> AsyncGenerator[AsyncClient, None]:
    app = build_fastapi_app(container=container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


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
        self, client: AsyncClient, user_token: str
    ) -> None:
        response = await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_saves_the_credential_for_the_authenticated_username(
        self, client: AsyncClient, user_token: str, container: Container
    ) -> None:
        await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        async with container.uow_factory() as uow:
            credential = await uow.external_credentials.find(
                username="alice", provider=Provider.PORTAL_TRANSPARENCIA
            )

        assert credential is not None
        assert credential.api_key == "test-api-key"


class TestGetCredentialAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get("/credentials")

        assert response.status_code == 401


class TestGetCredentialStatus:
    @pytest.mark.asyncio
    async def test_returns_not_configured_for_every_provider_by_default(
        self, client: AsyncClient, user_token: str
    ) -> None:
        response = await client.get(
            "/credentials", headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        assert response.json() == [
            {"configured": False, "provider": "KIPFLOW"},
            {"configured": False, "provider": "PORTAL_TRANSPARENCIA"},
        ]

    @pytest.mark.asyncio
    async def test_returns_configured_true_after_saving_a_credential(
        self, client: AsyncClient, user_token: str
    ) -> None:
        await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        response = await client.get(
            "/credentials", headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.json() == [
            {"configured": False, "provider": "KIPFLOW"},
            {"configured": True, "provider": "PORTAL_TRANSPARENCIA"},
        ]

    @pytest.mark.asyncio
    async def test_does_not_reflect_credentials_saved_by_other_users(
        self,
        client: AsyncClient,
        pyjwt_service: PyJWTService,
        user_token: str,
    ) -> None:
        other_user_token = pyjwt_service.create_access_token(username="bob")

        await client.post(
            "/credentials",
            json={"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"},
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

        response = await client.get(
            "/credentials", headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.json() == [
            {"configured": False, "provider": "KIPFLOW"},
            {"configured": False, "provider": "PORTAL_TRANSPARENCIA"},
        ]


class TestGetRevealCredential:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get("/credentials/KIPFLOW/reveal")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_the_key_the_caller_saved(
        self, client: AsyncClient, user_token: str
    ) -> None:
        headers = {"Authorization": f"Bearer {user_token}"}
        await client.post(
            "/credentials",
            json={"api_key": "my-kipflow-key", "provider": "KIPFLOW"},
            headers=headers,
        )

        response = await client.get("/credentials/KIPFLOW/reveal", headers=headers)

        assert response.status_code == 200
        assert response.json() == {"api_key": "my-kipflow-key"}

    @pytest.mark.asyncio
    async def test_returns_404_when_the_caller_saved_no_key_for_that_provider(
        self, client: AsyncClient, user_token: str
    ) -> None:
        response = await client.get(
            "/credentials/KIPFLOW/reveal",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404
        assert response.json()["type"] == "EXTERNAL_CREDENTIAL_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_never_reveals_a_key_saved_by_another_user(
        self, client: AsyncClient, user_token: str, pyjwt_service: PyJWTService
    ) -> None:
        other_token = pyjwt_service.create_access_token(username="bob")
        await client.post(
            "/credentials",
            json={"api_key": "bobs-key", "provider": "KIPFLOW"},
            headers={"Authorization": f"Bearer {other_token}"},
        )

        response = await client.get(
            "/credentials/KIPFLOW/reveal",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404
        assert "bobs-key" not in response.text

    @pytest.mark.asyncio
    async def test_unknown_provider_returns_422(
        self, client: AsyncClient, user_token: str
    ) -> None:
        response = await client.get(
            "/credentials/NOPE/reveal",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 422


class TestCredentialsRateLimit:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("get", "/credentials"),
            ("get", "/credentials/PORTAL_TRANSPARENCIA/reveal"),
            ("post", "/credentials"),
        ],
    )
    async def test_every_credentials_route_shares_one_bucket_per_user(
        self, client: AsyncClient, user_token: str, method: str, path: str
    ) -> None:
        headers = {"Authorization": f"Bearer {user_token}"}
        body = {"api_key": "test-api-key", "provider": "PORTAL_TRANSPARENCIA"}

        for _ in range(100):
            await client.get("/credentials", headers=headers)

        if method == "post":
            response = await client.post(path, json=body, headers=headers)
        else:
            response = await getattr(client, method)(path, headers=headers)

        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_exhausting_one_users_bucket_leaves_another_users_untouched(
        self, client: AsyncClient, user_token: str, pyjwt_service: PyJWTService
    ) -> None:
        headers = {"Authorization": f"Bearer {user_token}"}
        other_token = pyjwt_service.create_access_token(username="bob")
        other_headers = {"Authorization": f"Bearer {other_token}"}

        for _ in range(100):
            await client.get("/credentials", headers=headers)

        blocked = await client.get("/credentials", headers=headers)
        untouched = await client.get("/credentials", headers=other_headers)

        assert blocked.status_code == 429
        assert untouched.status_code == 200
