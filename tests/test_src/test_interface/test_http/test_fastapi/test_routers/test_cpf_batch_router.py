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
from osint_engine.infrastructure.providers.kipflow.in_memory_rate_limiter import (
    InMemoryKipFlowRateLimiter,
)
from osint_engine.interface.http.fastapi.fastapi_app import build_fastapi_app
from osint_engine.interface.http.schemas.batch_schema import BatchCPFResultSchema

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from osint_engine.infrastructure.services.pyjwt_service import PyJWTService
    from tests.conftest import MakeMemStorage
    from tests.test_src.test_interface.test_http.test_fastapi.conftest import (
        MakeContainer,
    )

CPF_1 = "10000000000"
CPF_2 = "10000000001"
CPF_3 = "10000000002"


@pytest_asyncio.fixture
async def batch_client(
    make_container: MakeContainer,
    make_mem_storage: MakeMemStorage,
) -> AsyncGenerator[tuple[AsyncClient, list[str]], None]:
    kipflow_calls: list[str] = []

    def handler(request: Request) -> Response:
        cpf = request.url.params["cpf"]
        kipflow_calls.append(cpf)

        if cpf == CPF_2:
            return Response(402)

        return Response(
            200, json={"success": True, "data": {"cpf": cpf, "nome": "FULANO DE TAL"}}
        )

    async with AsyncClient(transport=MockTransport(handler)) as kipflow_http_client:
        container = make_container(
            http_client=kipflow_http_client, mem_storage=make_mem_storage()
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
            yield client, kipflow_calls


@pytest.fixture
def admin_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="admin", role=Role.ADMIN)


@pytest.fixture
def viewer_token(pyjwt_service: PyJWTService) -> str:
    return pyjwt_service.create_access_token(username="viewer", role=Role.VIEWER)


class TestBatchEstimateValidation:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "body",
        [
            pytest.param({"cpfs": []}, id="empty"),
            pytest.param(
                {"cpfs": [f"100000000{i:02d}" for i in range(51)]}, id="fifty-one"
            ),
        ],
    )
    async def test_rejects_out_of_range_batches_without_calling_the_provider(
        self,
        batch_client: tuple[AsyncClient, list[str]],
        admin_token: str,
        body: dict[str, object],
    ) -> None:
        client, kipflow_calls = batch_client
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = await client.post("/cpf/batch/estimate", json=body, headers=headers)

        assert response.status_code == 422
        assert kipflow_calls == []


class TestBatchEstimate:
    @pytest.mark.asyncio
    async def test_returns_the_three_buckets_for_a_fresh_batch(
        self, batch_client: tuple[AsyncClient, list[str]], admin_token: str
    ) -> None:
        client, _ = batch_client
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = await client.post(
            "/cpf/batch/estimate",
            json={"cpfs": [CPF_1, CPF_2, CPF_3]},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == {
            "already_fetched": [],
            "billable": [CPF_1, CPF_2, CPF_3],
            "invalid": [],
            "wait_seconds": 0,
        }

    @pytest.mark.asyncio
    async def test_splits_invalid_cpfs_into_their_own_bucket(
        self, batch_client: tuple[AsyncClient, list[str]], admin_token: str
    ) -> None:
        client, _ = batch_client
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = await client.post(
            "/cpf/batch/estimate",
            json={"cpfs": ["123", CPF_1]},
            headers=headers,
        )

        assert response.status_code == 200
        assert response.json() == {
            "already_fetched": [],
            "billable": [CPF_1],
            "invalid": ["123"],
            "wait_seconds": 0,
        }


class _FrozenClock:
    def tick(self) -> float:
        return 0.0


class TestBatchEstimateWait:
    @pytest.mark.asyncio
    async def test_reports_the_limiter_forecast_when_the_second_bucket_is_saturated(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        admin_token: str,
    ) -> None:
        limiter = InMemoryKipFlowRateLimiter(now=_FrozenClock().tick)
        credential = ExternalCredential(
            api_key="test-api-key", provider=Provider.KIPFLOW, username="admin"
        )
        container = make_container(
            mem_storage=make_mem_storage(), kipflow_rate_limiter=limiter
        )

        async with container.uow_factory() as uow:
            await uow.external_credentials.save(credential=credential)

        for _ in range(5):
            await limiter.acquire(credential=credential)

        app = build_fastapi_app(container=container)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/cpf/batch/estimate",
                json={"cpfs": [CPF_1]},
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == 200
        assert response.json() == {
            "already_fetched": [],
            "billable": [CPF_1],
            "invalid": [],
            "wait_seconds": 1,
        }

    @pytest.mark.asyncio
    async def test_reports_zero_wait_when_the_caller_has_no_kipflow_credential(
        self,
        make_container: MakeContainer,
        make_mem_storage: MakeMemStorage,
        admin_token: str,
    ) -> None:
        limiter = InMemoryKipFlowRateLimiter(now=_FrozenClock().tick)
        container = make_container(
            mem_storage=make_mem_storage(), kipflow_rate_limiter=limiter
        )
        app = build_fastapi_app(container=container)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/cpf/batch/estimate",
                json={"cpfs": [CPF_1]},
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        assert response.status_code == 200
        assert response.json() == {
            "already_fetched": [],
            "billable": [CPF_1],
            "invalid": [],
            "wait_seconds": 0,
        }


class TestBatchRoleGuard:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path", "body"),
        [
            ("post", "/cpf/batch/estimate", {"cpfs": [CPF_1]}),
            ("post", "/cpf/batch", {"cpfs": [CPF_1]}),
            ("get", f"/cpf/{CPF_1}", None),
        ],
    )
    async def test_viewer_token_returns_403_on_every_cpf_route(
        self,
        batch_client: tuple[AsyncClient, list[str]],
        viewer_token: str,
        method: str,
        path: str,
        body: dict[str, object] | None,
    ) -> None:
        client, _ = batch_client
        headers = {"Authorization": f"Bearer {viewer_token}"}

        if body is None:
            response = await getattr(client, method)(path, headers=headers)
        else:
            response = await getattr(client, method)(path, json=body, headers=headers)

        assert response.status_code == 403

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("method", "path", "body"),
        [
            ("post", "/cpf/batch/estimate", {"cpfs": [CPF_1]}),
            ("post", "/cpf/batch", {"cpfs": [CPF_1]}),
            ("get", f"/cpf/{CPF_1}", None),
        ],
    )
    async def test_admin_token_returns_200_on_every_cpf_route(
        self,
        batch_client: tuple[AsyncClient, list[str]],
        admin_token: str,
        method: str,
        path: str,
        body: dict[str, object] | None,
    ) -> None:
        client, _ = batch_client
        headers = {"Authorization": f"Bearer {admin_token}"}

        if body is None:
            response = await getattr(client, method)(path, headers=headers)
        else:
            response = await getattr(client, method)(path, json=body, headers=headers)

        assert response.status_code == 200


class TestBatchExpansion:
    @pytest.mark.asyncio
    async def test_partial_failure_persists_the_successes_and_reports_per_item(
        self, batch_client: tuple[AsyncClient, list[str]], admin_token: str
    ) -> None:
        client, kipflow_calls = batch_client
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = await client.post(
            "/cpf/batch", json={"cpfs": [CPF_1, CPF_2, CPF_3]}, headers=headers
        )

        assert response.status_code == 200

        result = BatchCPFResultSchema.model_validate(response.json())

        assert [outcome.status for outcome in result.outcomes] == [
            "expanded",
            "failed",
            "expanded",
        ]
        assert result.outcomes[1].error_code == "PROVIDER_INSUFFICIENT_CREDITS"
        assert result.graph is not None
        person_ids = {
            str(node.id) for node in result.graph.nodes if node.type == "person"
        }
        assert person_ids != set()
        assert kipflow_calls == [CPF_1, CPF_2, CPF_3]

        catalog = await client.get("/graphs", headers=headers)

        assert catalog.status_code == 200
        entries = catalog.json()["entries"]
        assert len(entries) == 2
        assert {entry["root"]["id"] for entry in entries} == person_ids
