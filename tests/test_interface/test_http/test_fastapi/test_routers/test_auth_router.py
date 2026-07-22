from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from jwt import decode as jwt_decode  # pyright: ignore[reportUnknownVariableType]

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.config.settings import Settings

_TOKEN_EXPIRY_TOLERANCE_SECONDS = 5


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
    async def test_access_token_carries_authenticated_user_claims(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.post(
            "/auth/token",
            data={"username": "admin", "password": settings.admin_password},
        )
        access_token = response.json()["access_token"]

        claims = jwt_decode(
            jwt=access_token, key=settings.secret_key, algorithms=["HS256"]
        )

        assert claims["sub"] == "admin"

        assert claims["role"] == "ADMIN"

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


class TestPostTokenRateLimit:
    @pytest.mark.asyncio
    async def test_exceeding_attempt_limit_returns_429(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        attempt = {"username": "admin", "password": "wrong_password"}

        for _ in range(5):
            await fastapi_app_client.post("/auth/token", data=attempt)

        response = await fastapi_app_client.post("/auth/token", data=attempt)

        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_within_attempt_limit_is_not_blocked(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        attempt = {"username": "admin", "password": "wrong_password"}

        for _ in range(4):
            response = await fastapi_app_client.post("/auth/token", data=attempt)

            assert response.status_code == 401


class TestPostViewerToken:
    @pytest.mark.asyncio
    async def test_returns_200_without_body(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post("/auth/viewer-token")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_response_includes_access_token(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.post("/auth/viewer-token")
        body: dict[str, object] = response.json()

        assert "access_token" in body

        assert isinstance(body["access_token"], str)

        assert len(body["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_access_token_carries_viewer_claims(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.post("/auth/viewer-token")
        access_token = response.json()["access_token"]

        claims = jwt_decode(
            jwt=access_token, key=settings.secret_key, algorithms=["HS256"]
        )

        assert claims["sub"] == "visitor"

        assert claims["role"] == "VIEWER"

    @pytest.mark.asyncio
    async def test_access_token_expires_using_viewer_ttl(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.post("/auth/viewer-token")
        access_token = response.json()["access_token"]

        claims = jwt_decode(
            jwt=access_token, key=settings.secret_key, algorithms=["HS256"]
        )
        expires_in_seconds = claims["exp"] - datetime.now(tz=UTC).timestamp()
        expected_seconds = settings.viewer_token_expire_minutes * 60

        assert (
            abs(expires_in_seconds - expected_seconds) < _TOKEN_EXPIRY_TOLERANCE_SECONDS
        )

        assert (
            settings.viewer_token_expire_minutes != settings.access_token_expire_minutes
        )


class TestPostViewerTokenRateLimit:
    @pytest.mark.asyncio
    async def test_exceeding_issuance_limit_returns_429(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        for _ in range(20):
            await fastapi_app_client.post("/auth/viewer-token")

        response = await fastapi_app_client.post("/auth/viewer-token")

        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_429_response_includes_retry_after_header(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        for _ in range(20):
            await fastapi_app_client.post("/auth/viewer-token")

        response = await fastapi_app_client.post("/auth/viewer-token")

        assert response.headers.get("retry-after") is not None

        assert int(response.headers["retry-after"]) > 0
