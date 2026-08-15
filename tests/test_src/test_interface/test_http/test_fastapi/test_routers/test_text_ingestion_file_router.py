from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient
from openpyxl import Workbook

from osint_engine.application.auth.user import Role
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.text_ingestion import spreadsheet_reader
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

_VALID_CPF_DIGITS = "11144477735"


def _xlsx_bytes(*, cell_value: str) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet["A1"] = cell_value
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


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


class TestPostTextIngestionFileAuthentication:
    @pytest.mark.asyncio
    async def test_missing_token_returns_401(self, client: AsyncClient) -> None:
        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.xlsx", _xlsx_bytes(cell_value=_VALID_CPF_DIGITS))},
            data={"patterns": ["CPF_LOOSE"]},
        )

        assert response.status_code == 401


class TestPostTextIngestionFileAuthorization:
    @pytest.mark.asyncio
    async def test_viewer_token_returns_403(
        self, client: AsyncClient, viewer_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.xlsx", _xlsx_bytes(cell_value=_VALID_CPF_DIGITS))},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )

        assert response.status_code == 403


class TestPostTextIngestionFile:
    @pytest.mark.asyncio
    async def test_valid_xlsx_returns_200_with_a_person_stub_per_cpf(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.xlsx", _xlsx_bytes(cell_value=_VALID_CPF_DIGITS))},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 200

        graph = GraphSchema.model_validate(response.json())

        assert any(node.type == "person" for node in graph.nodes)

    @pytest.mark.asyncio
    async def test_matches_the_json_endpoint_result_for_the_same_text(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        headers = {"Authorization": f"Bearer {valid_token}"}

        file_response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.xlsx", _xlsx_bytes(cell_value=_VALID_CPF_DIGITS))},
            data={"patterns": ["CPF_LOOSE"]},
            headers=headers,
        )
        json_response = await client.post(
            "/text-ingestion",
            json={"text": _VALID_CPF_DIGITS, "patterns": ["CPF_LOOSE"]},
            headers=headers,
        )

        file_graph = GraphSchema.model_validate(file_response.json())
        json_graph = GraphSchema.model_validate(json_response.json())

        assert {node.id for node in file_graph.nodes} == {
            node.id for node in json_graph.nodes
        }


class TestPostTextIngestionFileErrors:
    @pytest.mark.asyncio
    async def test_unsupported_file_type_returns_422(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.txt", b"irrelevant")},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_oversized_file_returns_422(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        content = b"x" * (10 * 1024 * 1024 + 1)

        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.csv", content)},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_corrupted_xlsx_returns_422(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.xlsx", b"not a zip file")},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_csv_field_above_the_csv_module_limit_returns_422(
        self, client: AsyncClient, valid_token: str
    ) -> None:
        content = b"a," + b"x" * 200_000

        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.csv", content)},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_too_many_rows_returns_422(
        self,
        client: AsyncClient,
        valid_token: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(spreadsheet_reader, "_MAX_ROWS_PER_SHEET", 1)

        response = await client.post(
            "/text-ingestion/file",
            files={"file": ("data.csv", b"a\nb\nc")},
            data={"patterns": ["CPF_LOOSE"]},
            headers={"Authorization": f"Bearer {valid_token}"},
        )

        assert response.status_code == 422


class TestPostTextIngestionFilePossiblyMatches:
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
            cpf=masked_overlapping_cpf(real_cpf=_VALID_CPF_DIGITS),
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
                "/text-ingestion/file",
                files={
                    "file": ("data.xlsx", _xlsx_bytes(cell_value=_VALID_CPF_DIGITS))
                },
                data={"patterns": ["CPF_LOOSE"]},
                headers={"Authorization": f"Bearer {valid_token}"},
            )

        assert response.status_code == 200

        graph = GraphSchema.model_validate(response.json())

        assert any(edge.type == "possibly_matches" for edge in graph.edges)
