from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.config.settings import Settings

# TESTS


class TestFastAPICORSConfiguration:
    """CORS preflight behavior wired in build_fastapi_app: allow_origins comes
    from settings, credentials/methods/headers are permissive by design."""

    @pytest.mark.asyncio
    async def test_preflight_reflects_configured_origin(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        origin = settings.cors_origins[0]

        response = await fastapi_app_client.options(
            "/auth/token",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.headers.get("access-control-allow-origin") == origin

    @pytest.mark.asyncio
    async def test_preflight_rejects_unconfigured_origin(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.options(
            "/auth/token",
            headers={
                "Origin": "http://not-allowed.example",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert "access-control-allow-origin" not in response.headers

    @pytest.mark.asyncio
    async def test_preflight_allows_credentials(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.options(
            "/auth/token",
            headers={
                "Origin": settings.cors_origins[0],
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.headers.get("access-control-allow-credentials") == "true"

    @pytest.mark.asyncio
    async def test_preflight_allows_requested_method(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.options(
            "/auth/token",
            headers={
                "Origin": settings.cors_origins[0],
                "Access-Control-Request-Method": "DELETE",
            },
        )

        assert "DELETE" in response.headers.get("access-control-allow-methods", "")

    @pytest.mark.asyncio
    async def test_preflight_allows_requested_header(
        self, fastapi_app_client: AsyncClient, settings: Settings
    ) -> None:
        response = await fastapi_app_client.options(
            "/auth/token",
            headers={
                "Origin": settings.cors_origins[0],
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "X-Custom-Header",
            },
        )

        assert (
            "x-custom-header"
            in response.headers.get("access-control-allow-headers", "").lower()
        )
