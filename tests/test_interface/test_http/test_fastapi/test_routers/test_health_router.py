from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
from httpx2 import ASGITransport, AsyncClient

from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app

if TYPE_CHECKING:
    from asyncpg import Pool

    from tests.test_interface.test_http.test_fastapi.conftest import MakeContainer


class _UnavailablePgPool:
    """A pool whose every query raises, standing in for an unreachable Postgres
    so the readiness probe's failure path can be exercised."""

    async def execute(self, query: str, *args: object) -> str:  # noqa: ARG002
        message = "connection refused"

        raise OSError(message)


# TESTS


class TestLiveness:
    @pytest.mark.asyncio
    async def test_returns_200_ok(self, fastapi_app_client: AsyncClient) -> None:
        response = await fastapi_app_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestReadiness:
    @pytest.mark.asyncio
    async def test_returns_200_ready_when_database_reachable(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.get("/health/ready")

        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    @pytest.mark.asyncio
    async def test_returns_503_not_ready_when_database_unavailable(
        self, make_container: MakeContainer
    ) -> None:
        container = make_container(pg_pool=cast("Pool", _UnavailablePgPool()))
        app = build_fastapi_app(container=container)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        assert response.json() == {"status": "not_ready"}
