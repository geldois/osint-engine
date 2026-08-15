from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient

from osint_engine.application.auth.user import Role
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

_TEXT_CPF = "111.444.777-35"
_VALID_CPF_TEXT = f"Contato: CPF {_TEXT_CPF}, favor confirmar."
_BUNDLE_ID = "brazilian_documents_v1"


@pytest_asyncio.fixture(loop_scope="session")
async def client(make_container: MakeContainer) -> AsyncGenerator[AsyncClient, None]:
    app = build_fastapi_app(container=make_container())

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role=Role.ADMIN)


@pytest.fixture
def viewer_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="visitor", role=Role.VIEWER)


class TestPostTextIngestionAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.post(
            "/text-ingestion",
            json={"text": _VALID_CPF_TEXT, "patterns": [_BUNDLE_ID]},
        )

        assert response.status_code == 401


class TestPostTextIngestionAuthorization:
    @pytest.mark.asyncio
    async def test_viewer_token_returns_403(
        self, client: AsyncClient, viewer_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion",
            json={"text": _VALID_CPF_TEXT, "patterns": [_BUNDLE_ID]},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )

        assert response.status_code == 403


class TestPostTextIngestion:
    @pytest.mark.asyncio
    async def test_valid_cpf_returns_200_with_graph_schema(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion",
            json={"text": _VALID_CPF_TEXT, "patterns": [_BUNDLE_ID]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200
        GraphSchema.model_validate(response.json())

    @pytest.mark.asyncio
    async def test_mixed_bundle_and_atomic_names_return_200(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion",
            json={
                "text": "Empresa CNPJ 11.222.333/0001-81 registrada",
                "patterns": [_BUNDLE_ID, "CNPJ_LOOSE"],
            },
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200

        graph = GraphSchema.model_validate(response.json())

        assert any(node.type == "company" for node in graph.nodes)

    @pytest.mark.asyncio
    async def test_returns_422_when_no_pattern_matches(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion",
            json={"text": "nada relevante aqui", "patterns": [_BUNDLE_ID]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_returns_422_for_an_unknown_pattern_name(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion",
            json={"text": _VALID_CPF_TEXT, "patterns": ["does_not_exist"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422


class TestGetTextPatterns:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.get("/text-ingestion/patterns")

        assert response.status_code == 401


class TestGetTextPatternsAuthorization:
    @pytest.mark.asyncio
    async def test_viewer_token_returns_403(
        self, client: AsyncClient, viewer_token: str
    ) -> None:
        response = await client.get(
            "/text-ingestion/patterns",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )

        assert response.status_code == 403


class TestGetTextPatternsSuccess:
    @pytest.mark.asyncio
    async def test_returns_200_with_the_atomic_catalog_and_default_bundle(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.get(
            "/text-ingestion/patterns",
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200

        body = response.json()

        assert {p["name"] for p in body["patterns"]} == {
            "CPF_LOOSE",
            "CPF_LABELED",
            "CNPJ_LOOSE",
            "CNPJ_LABELED",
            "CEP_AND_NUMBER",
        }
        assert any(bundle["id"] == _BUNDLE_ID for bundle in body["bundles"])


class TestPostTextIngestionPossiblyMatches:
    @pytest.mark.asyncio
    async def test_returns_possibly_matches_edge_when_a_masked_person_overlaps(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        make_entity_revision: MakeEntityRevision,
        valid_token: str,
    ) -> None:
        stored = Person(
            age_range="Entre 41 a 50 anos",
            birthdate=None,
            cpf=masked_overlapping_cpf(real_cpf=_TEXT_CPF),
            name="FULANO DE TAL",
            registration_date=None,
            registration_status=None,
        )
        container = make_container(
            mem_storage=make_mem_storage(nodes=[make_entity_revision(entity=stored)])
        )
        app = build_fastapi_app(container=container)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/text-ingestion",
                json={"text": _VALID_CPF_TEXT, "patterns": [_BUNDLE_ID]},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

        assert response.status_code == 200

        graph = GraphSchema.model_validate(response.json())

        assert any(edge.type == "possibly_matches" for edge in graph.edges)


class TestTextIngestionRateLimit:
    @pytest.mark.asyncio
    async def test_shared_bucket_returns_429_past_100_requests(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        headers = {"Authorization": f"Bearer {valid_token}"}
        body = {"text": _VALID_CPF_TEXT, "patterns": [_BUNDLE_ID]}

        for _ in range(100):
            await client.post("/text-ingestion", json=body, headers=headers)

        response = await client.post("/text-ingestion", json=body, headers=headers)

        assert response.status_code == 429
