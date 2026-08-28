from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.application.auth.user import Role
from osint_engine.application.use_cases.expansion.expand_by_legal_process import (
    ExpandByLegalProcess,
)
from osint_engine.infrastructure.providers.kipflow.endpoints.legal_process_fetcher import (  # noqa: E501
    KipFlowLegalProcessFetcher,
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

CPF = "10000000000"

_LEGAL_PROCESS_RECORD_DATA: dict[str, object] = {
    "numeroProcessoUnico": "0001234-56.2024.8.26.0100",
    "tribunal": "TJSP",
}

_SUCCESS_RESPONSE_DATA: dict[str, object] = {
    "success": True,
    "data": [_LEGAL_PROCESS_RECORD_DATA],
}


@pytest_asyncio.fixture
async def kipflow_http_client() -> AsyncGenerator[AsyncClient, None]:

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, json=_SUCCESS_RESPONSE_DATA)

    async with AsyncClient(transport=MockTransport(handler)) as http_client:
        yield http_client


@pytest.fixture
def legal_process_container(
    make_container: MakeContainer,
    make_mem_storage: MakeMemStorage,
    kipflow_http_client: AsyncClient,
) -> Container:
    return make_container(
        http_client=kipflow_http_client,
        mem_storage=make_mem_storage(),
    )


@pytest_asyncio.fixture
async def client(
    legal_process_container: Container,
) -> AsyncGenerator[AsyncClient, None]:
    credential = ExternalCredential(
        api_key="test-api-key", provider=Provider.KIPFLOW, username="admin"
    )

    async with legal_process_container.uow_factory() as uow:
        await uow.external_credentials.save(credential=credential)

    app = build_fastapi_app(container=legal_process_container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role=Role.ADMIN)


class TestGetLegalProcessAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get(f"/legal-process/{CPF}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_viewer_token_is_rejected(
        self, client: AsyncClient, pyjwt_service: PyJWTService
    ) -> None:
        viewer_token = pyjwt_service.create_access_token(
            username="viewer", role=Role.VIEWER
        )

        response = await client.get(
            f"/legal-process/{CPF}",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )

        assert response.status_code == 403


class TestGetLegalProcessExpansion:
    @pytest.mark.asyncio
    async def test_valid_token_and_known_credential_returns_graph_schema(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/legal-process/{CPF}",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        GraphSchema.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_returns_204_when_no_processes_are_found(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        valid_token: str,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json={"success": True, "data": []})

        async with AsyncClient(transport=MockTransport(handler)) as http_client:
            container = make_container(
                http_client=http_client, mem_storage=make_mem_storage()
            )
            credential = ExternalCredential(
                api_key="test-api-key", provider=Provider.KIPFLOW, username="admin"
            )

            async with container.uow_factory() as uow:
                await uow.external_credentials.save(credential=credential)

            app = build_fastapi_app(container=container)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/legal-process/{CPF}",
                    headers={"Authorization": f"Bearer {valid_token}"},
                )

        assert response.status_code == 204


class TestLegalProcessCompositionRoot:
    def test_container_resolves_legal_process_fetcher_and_use_case(
        self, legal_process_container: Container
    ) -> None:
        assert isinstance(
            legal_process_container.fetchers.legal_process_fetcher,
            KipFlowLegalProcessFetcher,
        )

        use_case = legal_process_container.use_cases.expand_by_legal_process(
            cpf_or_cnpj=CPF, username="admin"
        )

        assert isinstance(use_case, ExpandByLegalProcess)
