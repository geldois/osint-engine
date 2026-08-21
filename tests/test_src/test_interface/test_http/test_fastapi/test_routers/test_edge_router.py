from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

if TYPE_CHECKING:
    from httpx2 import AsyncClient

    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService


@pytest.fixture
def viewer_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="viewer", role="VIEWER")


class TestGetEdgeHistoryAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.get(f"/edges/{uuid4()}/history")

        assert response.status_code == 401


class TestGetEdgeHistoryReadAccess:
    @pytest.mark.asyncio
    async def test_viewer_token_returns_200_with_empty_list_for_an_unknown_id(
        self, fastapi_app_client: AsyncClient, viewer_token: str
    ) -> None:
        response = await fastapi_app_client.get(
            f"/edges/{uuid4()}/history",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )

        assert response.status_code == 200
        assert response.json() == []
