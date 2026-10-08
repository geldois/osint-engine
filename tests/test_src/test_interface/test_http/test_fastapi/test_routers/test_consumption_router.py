from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from httpx2 import ASGITransport, AsyncClient

from osint_engine.domain.entities.nodes.person import Person
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from uuid import UUID

    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.conftest import MakeEntityRecord, MakeMemStorage
    from tests.test_src.test_interface.test_http.test_fastapi.conftest import (
        MakeContainer,
    )

_CPF = "10000000000"


def _person_id() -> UUID:
    return Person(
        age_range=None,
        birthdate=None,
        cpf=_CPF,
        name=None,
        registration_date=None,
        registration_status=None,
    ).id


@pytest_asyncio.fixture(loop_scope="session")
async def client(
    make_container: MakeContainer,
    make_mem_storage: MakeMemStorage,
    make_entity_record: MakeEntityRecord,
) -> AsyncGenerator[AsyncClient, None]:
    person_id = _person_id()
    records = [
        make_entity_record(entity_id=person_id, username="alice"),
        make_entity_record(entity_id=person_id, username="bob"),
        make_entity_record(entity_id=person_id, username="bob"),
    ]
    container = make_container(mem_storage=make_mem_storage(entity_records=records))

    async with AsyncClient(
        transport=ASGITransport(app=build_fastapi_app(container=container)),
        base_url="http://test",
    ) as client:
        yield client


def _headers(pyjwt_service: PyJWTService, username: str) -> dict[str, str]:
    token = pyjwt_service.create_access_token(username=username)

    return {"Authorization": f"Bearer {token}"}


class TestGetConsumptionCatalog:
    @pytest.mark.asyncio
    async def test_returns_only_the_callers_entries(
        self, client: AsyncClient, pyjwt_service: PyJWTService
    ) -> None:
        alice = await client.get(
            "/consumption", headers=_headers(pyjwt_service, "alice")
        )
        bob = await client.get("/consumption", headers=_headers(pyjwt_service, "bob"))

        assert [entry["username"] for entry in alice.json()] == ["alice"]
        assert [entry["username"] for entry in bob.json()] == ["bob", "bob"]

    @pytest.mark.asyncio
    async def test_a_user_with_no_requests_gets_an_empty_list(
        self, client: AsyncClient, pyjwt_service: PyJWTService
    ) -> None:
        response = await client.get(
            "/consumption", headers=_headers(pyjwt_service, "carol")
        )

        assert response.status_code == 200
        assert response.json() == []


class TestGetConsumptionByCpf:
    @pytest.mark.asyncio
    async def test_returns_only_the_callers_entries_for_that_cpf(
        self, client: AsyncClient, pyjwt_service: PyJWTService
    ) -> None:
        alice = await client.get(
            f"/consumption/{_CPF}", headers=_headers(pyjwt_service, "alice")
        )
        carol = await client.get(
            f"/consumption/{_CPF}", headers=_headers(pyjwt_service, "carol")
        )

        assert [entry["username"] for entry in alice.json()] == ["alice"]
        assert carol.json() == []
