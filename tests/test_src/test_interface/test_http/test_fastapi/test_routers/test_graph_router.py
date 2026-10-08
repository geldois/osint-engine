from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from httpx2 import ASGITransport, AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app
from osint_engine.interface.http.schemas.graph_schema import GraphSchema

if TYPE_CHECKING:
    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.conftest import MakeMemStorage
    from tests.test_src.test_interface.test_http.test_fastapi.conftest import (
        MakeContainer,
    )

CPF = "10000000000"


@pytest.fixture
def user_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="alice")


class TestGetGraphHistoryAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.get(f"/graphs/{uuid4()}/history")

        assert response.status_code == 401


class TestGetGraphCatalogAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(
        self, fastapi_app_client: AsyncClient
    ) -> None:
        response = await fastapi_app_client.get("/graphs")

        assert response.status_code == 401


class TestGetGraphCatalogReadAccess:
    @pytest.mark.asyncio
    async def test_authenticated_user_gets_200_with_no_entries_when_nothing_was_fetched(
        self, fastapi_app_client: AsyncClient, user_token: str
    ) -> None:
        response = await fastapi_app_client.get(
            "/graphs", headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 200
        assert response.json() == {"entries": []}


class TestGetGraphHistoryReadAccess:
    @pytest.mark.asyncio
    async def test_authenticated_user_gets_200_for_an_unseen_root_id(
        self, fastapi_app_client: AsyncClient, user_token: str
    ) -> None:
        response = await fastapi_app_client.get(
            f"/graphs/{uuid4()}/history",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        assert response.json() == []


class TestGetGraphHistorySmoke:
    @pytest.mark.asyncio
    async def test_returns_both_revisions_after_two_real_cpf_expansions(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        user_token: str,
    ) -> None:
        payloads: list[dict[str, object]] = [
            {"success": True, "data": {"cpf": CPF, "nome": "FULANO DE TAL"}},
            {"success": True, "data": {"cpf": CPF, "nome": "FULANO DE TAL SILVA"}},
        ]
        pending = iter(payloads)

        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=next(pending))

        async with AsyncClient(transport=MockTransport(handler)) as kipflow_http_client:
            container = make_container(
                http_client=kipflow_http_client, mem_storage=make_mem_storage()
            )
            credential = ExternalCredential(
                api_key="test-api-key", provider=Provider.KIPFLOW, username="alice"
            )

            async with container.uow_factory() as uow:
                await uow.external_credentials.save(credential=credential)

            app = build_fastapi_app(container=container)
            headers = {"Authorization": f"Bearer {user_token}"}

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                first = await client.get(f"/cpf/{CPF}", headers=headers)
                second = await client.get(f"/cpf/{CPF}?force=true", headers=headers)

                assert first.status_code == 200
                assert second.status_code == 200

                root_id = GraphSchema.model_validate(first.json()).root_id

                history_response = await client.get(
                    f"/graphs/{root_id}/history", headers=headers
                )

        assert history_response.status_code == 200

        history = [GraphSchema.model_validate(item) for item in history_response.json()]

        assert len(history) == 2
        assert {graph.root_id for graph in history} == {root_id}


class TestGetGraphCatalogSmoke:
    @pytest.mark.asyncio
    async def test_lists_one_entry_with_revision_count_two_after_force_re_expansion(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        user_token: str,
    ) -> None:
        payloads: list[dict[str, object]] = [
            {"success": True, "data": {"cpf": CPF, "nome": "FULANO DE TAL"}},
            {"success": True, "data": {"cpf": CPF, "nome": "FULANO DE TAL SILVA"}},
        ]
        pending = iter(payloads)

        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=next(pending))

        async with AsyncClient(transport=MockTransport(handler)) as kipflow_http_client:
            container = make_container(
                http_client=kipflow_http_client, mem_storage=make_mem_storage()
            )
            credential = ExternalCredential(
                api_key="test-api-key", provider=Provider.KIPFLOW, username="alice"
            )

            async with container.uow_factory() as uow:
                await uow.external_credentials.save(credential=credential)

            app = build_fastapi_app(container=container)
            headers = {"Authorization": f"Bearer {user_token}"}

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                first = await client.get(f"/cpf/{CPF}", headers=headers)
                second = await client.get(f"/cpf/{CPF}?force=true", headers=headers)

                assert first.status_code == 200
                assert second.status_code == 200

                root_id = GraphSchema.model_validate(first.json()).root_id

                catalog_response = await client.get("/graphs", headers=headers)

        assert catalog_response.status_code == 200

        entries = catalog_response.json()["entries"]

        assert len(entries) == 1
        assert entries[0]["revision_count"] == 2
        assert entries[0]["root"]["id"] == str(root_id)


class TestGraphCatalogRateLimit:
    @pytest.mark.asyncio
    async def test_exhausting_one_users_bucket_leaves_another_users_untouched(
        self,
        fastapi_app_client: AsyncClient,
        user_token: str,
        pyjwt_service: PyJWTService,
    ) -> None:
        headers = {"Authorization": f"Bearer {user_token}"}
        other_token = pyjwt_service.create_access_token(username="bob")
        other_headers = {"Authorization": f"Bearer {other_token}"}

        for _ in range(100):
            await fastapi_app_client.get("/graphs", headers=headers)

        blocked = await fastapi_app_client.get("/graphs", headers=headers)
        untouched = await fastapi_app_client.get("/graphs", headers=other_headers)

        assert blocked.status_code == 429
        assert untouched.status_code == 200
