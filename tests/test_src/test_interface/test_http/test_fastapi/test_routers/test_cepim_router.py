from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.application.use_cases.expansion.expand_by_cepim import ExpandByCEPIM
from osint_engine.infrastructure.providers.portal_transparencia.endpoints.cepim_fetcher import (  # noqa: E501
    PortalTransparenciaCEPIMFetcher,
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

_CEPIM_RECORD_DATA = {
    "dataReferencia": "10/08/2026",
    "id": 4242,
    "motivo": "Prestação de contas rejeitada",
    "orgaoSuperior": {"nome": "Ministério da Cidadania"},
    "pessoaJuridica": {
        "cnpjFormatado": "33.754.482/0001-24",
        "nomeFantasiaReceita": "ONG FANTASIA",
        "razaoSocialReceita": "ONG SEM FINS LUCRATIVOS",
    },
}

CNPJ = "33754482000124"


@pytest.fixture
def captured_request_url() -> dict[str, str]:
    return {}


@pytest_asyncio.fixture
async def portal_transparencia_http_client(
    captured_request_url: dict[str, str],
) -> AsyncGenerator[AsyncClient, None]:

    def handler(request: Request) -> Response:
        captured_request_url["url"] = str(request.url)

        if request.url.query:
            return Response(200, json=[_CEPIM_RECORD_DATA])

        return Response(200, json=_CEPIM_RECORD_DATA)

    async with AsyncClient(transport=MockTransport(handler)) as http_client:
        yield http_client


@pytest.fixture
def cepim_container(
    make_container: MakeContainer,
    make_mem_storage: MakeMemStorage,
    portal_transparencia_http_client: AsyncClient,
) -> Container:
    return make_container(
        http_client=portal_transparencia_http_client,
        mem_storage=make_mem_storage(),
    )


@pytest_asyncio.fixture
async def client(cepim_container: Container) -> AsyncGenerator[AsyncClient, None]:
    credential = ExternalCredential(
        api_key="test-api-key",
        provider=Provider.PORTAL_TRANSPARENCIA,
        username="admin",
    )

    async with cepim_container.uow_factory() as uow:
        await uow.external_credentials.save(credential=credential)

    app = build_fastapi_app(container=cepim_container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role="admin")


class TestGetCEPIMAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get(f"/cepim/{CNPJ}")

        assert response.status_code == 401


class TestGetCEPIMExpansion:
    @pytest.mark.asyncio
    async def test_valid_token_and_known_credential_returns_graph_schema(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/cepim/{CNPJ}", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 200
        GraphSchema.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_returns_204_when_no_sanctions_are_found(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        valid_token: str,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=[])

        async with AsyncClient(transport=MockTransport(handler)) as http_client:
            container = make_container(
                http_client=http_client, mem_storage=make_mem_storage()
            )
            credential = ExternalCredential(
                api_key="test-api-key",
                provider=Provider.PORTAL_TRANSPARENCIA,
                username="admin",
            )

            async with container.uow_factory() as uow:
                await uow.external_credentials.save(credential=credential)

            app = build_fastapi_app(container=container)

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    f"/cepim/{CNPJ}",
                    headers={"Authorization": f"Bearer {valid_token}"},
                )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_accepts_cepim_id_as_an_optional_query_parameter(
        self,
        captured_request_url: dict[str, str],
        client: AsyncClient,
        valid_token: str,
    ) -> None:
        response = await client.get(
            f"/cepim/{CNPJ}",
            params={"cepim_id": 42},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        assert captured_request_url["url"].endswith("cepim/42")


class TestCEPIMCompositionRoot:
    def test_container_resolves_cepim_fetcher_and_use_case(
        self, cepim_container: Container
    ) -> None:
        assert isinstance(
            cepim_container.fetchers.cepim_fetcher, PortalTransparenciaCEPIMFetcher
        )

        use_case = cepim_container.use_cases.expand_by_cepim(
            cnpj=CNPJ,
            cepim_id=None,
            username="admin",
        )

        assert isinstance(use_case, ExpandByCEPIM)
