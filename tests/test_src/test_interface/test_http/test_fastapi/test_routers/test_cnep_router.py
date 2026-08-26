from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app
from osint_engine.interface.http.schemas.graph_schema import GraphSchema
from tests.test_src.test_interface.test_http.test_fastapi.conftest import (
    masked_overlapping_cpf,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.conftest import MakeEntityRevision, MakeMemStorage
    from tests.test_src.test_interface.test_http.test_fastapi.conftest import (
        MakeContainer,
    )

_CNEP_RECORD_DATA = {
    "dataFimSancao": "2026-01-01",
    "dataInicioSancao": "2024-01-01",
    "dataPublicacaoSancao": "2024-01-15",
    "fundamentacao": [{"codigo": "1", "descricao": "Lei 8.666/1993, art. 87"}],
    "id": 359510,
    "linkPublicacao": "https://portaldatransparencia.gov.br/sancoes/cnep/123",
    "numeroProcesso": "123/2024",
    "orgaoSancionador": {"nome": "CGU"},
    "pessoa": {
        "cnpjFormatado": "33.754.482/0001-24",
        "nomeFantasiaReceita": "EMPRESA FANTASIA",
        "razaoSocialReceita": "EMPRESA LTDA",
    },
    "tipoSancao": {"descricaoResumida": "Suspensão"},
    "valorMulta": "1.000,50",
}

_PF_CNEP_RECORD_DATA = {
    **_CNEP_RECORD_DATA,
    "pessoa": {
        "cpfFormatado": "100.000.000-00",
        "nome": "FULANO DE TAL",
    },
}

CPF_OR_CNPJ = "33754482000124"

PERSON_CPF = "10000000000"


@pytest_asyncio.fixture(loop_scope="session")
async def portal_transparencia_http_client() -> AsyncGenerator[AsyncClient, None]:

    def handler(request: Request) -> Response:  # noqa: ARG001
        return Response(200, json=[_CNEP_RECORD_DATA])

    async with AsyncClient(transport=MockTransport(handler)) as http_client:
        yield http_client


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    make_container: MakeContainer,
    make_mem_storage: MakeMemStorage,
    portal_transparencia_http_client: AsyncClient,
) -> AsyncGenerator[AsyncClient, None]:
    credential = ExternalCredential(
        api_key="test-api-key",
        provider=Provider.PORTAL_TRANSPARENCIA,
        username="admin",
    )
    mem_storage = make_mem_storage()

    container = make_container(
        http_client=portal_transparencia_http_client, mem_storage=mem_storage
    )

    async with container.uow_factory() as uow:
        await uow.external_credentials.save(credential=credential)

    app = build_fastapi_app(container=container)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role="admin")


class TestGetCnepAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get(f"/cnep/{CPF_OR_CNPJ}")

        assert response.status_code == 401


class TestGetCnepExpansion:
    @pytest.mark.asyncio
    async def test_valid_token_and_known_credential_returns_200(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            f"/cnep/{CPF_OR_CNPJ}", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 200

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
                    f"/cnep/{CPF_OR_CNPJ}",
                    headers={"Authorization": f"Bearer {valid_token}"},
                )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_unknown_credential_returns_404(
        self, client: AsyncClient, pyjwt_service: PyJWTService
    ) -> None:
        token = pyjwt_service.create_access_token(username="stranger", role="admin")

        response = await client.get(
            f"/cnep/{CPF_OR_CNPJ}", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_invalid_cpf_or_cnpj_returns_422(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            "/cnep/123", headers={"Authorization": f"Bearer {valid_token}"}
        )

        assert response.status_code == 422


class TestGetCnepPossiblyMatches:
    @pytest.mark.asyncio
    async def test_returns_possibly_matches_edge_when_a_masked_person_overlaps(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        make_entity_revision: MakeEntityRevision,
        valid_token: str,
    ) -> None:
        def handler(request: Request) -> Response:  # noqa: ARG001
            return Response(200, json=[_PF_CNEP_RECORD_DATA])

        stored = Person(
            age_range="Entre 41 a 50 anos",
            birthdate=None,
            cpf=masked_overlapping_cpf(real_cpf=PERSON_CPF),
            name="FULANO DE TAL",
            registration_date=None,
            registration_status=None,
        )

        async with AsyncClient(transport=MockTransport(handler)) as http_client:
            container = make_container(
                http_client=http_client,
                mem_storage=make_mem_storage(
                    nodes=[make_entity_revision(entity=stored)]
                ),
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
                    f"/cnep/{PERSON_CPF}",
                    headers={"Authorization": f"Bearer {valid_token}"},
                )

        assert response.status_code == 200

        graph = GraphSchema.model_validate(response.json())

        assert any(edge.type == "possibly_matches" for edge in graph.edges)
