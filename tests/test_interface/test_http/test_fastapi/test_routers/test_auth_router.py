from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.config.settings import Settings


class TestPostToken:
    @pytest.mark.asyncio
    async def test_valid_credentials_return_200(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "admin", "password": settings.admin_password},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_valid_credentials_response_includes_access_token(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "admin", "password": settings.admin_password},
        )
        body: dict[str, object] = response.json()

        assert "access_token" in body

        assert isinstance(body["access_token"], str)

        assert len(body["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_invalid_password_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrong_password"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_unknown_username_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "nobody", "password": "any_password"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_failed_auth_includes_www_authenticate_bearer(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrong_password"},
        )

        assert response.headers.get("WWW-Authenticate") == "Bearer"

    @pytest.mark.asyncio
    async def test_failed_auth_response_carries_correlation_id(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrong_password"},
        )

        assert "x-correlation-id" in response.headers
