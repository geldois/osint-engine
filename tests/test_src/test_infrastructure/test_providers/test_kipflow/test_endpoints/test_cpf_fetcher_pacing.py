from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest
from httpx2 import AsyncClient, MockTransport, Request, Response

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.providers.kipflow.endpoints.cpf_fetcher import (
    KipFlowCPFFetcher,
)
from osint_engine.infrastructure.providers.kipflow.in_memory_rate_limiter import (
    InMemoryKipFlowRateLimiter,
)

if TYPE_CHECKING:
    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.graph import Graph

CPF = "10000000000"


class _FakeClock:
    def __init__(self) -> None:
        self._now = 0.0
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self._now

    async def sleep(self, delay: float) -> None:
        self.sleeps.append(delay)
        self._now += delay
        await asyncio.sleep(0)


class TestKipFlowCPFFetcherPacing:
    @pytest.mark.asyncio
    async def test_the_fetcher_waits_for_the_rate_limiter_before_calling_kipflow(
        self,
    ) -> None:
        clock = _FakeClock()
        limiter = InMemoryKipFlowRateLimiter(now=clock.now, sleep=clock.sleep)
        credential = ExternalCredential(
            api_key="test-api-key", provider=Provider.KIPFLOW, username="analyst"
        )
        calls_at: list[float] = []

        def handler(request: Request) -> Response:  # noqa: ARG001
            calls_at.append(clock.now())

            return Response(
                200,
                json={"success": True, "data": {"cpf": CPF, "nome": "FULANO DE TAL"}},
            )

        fetcher = KipFlowCPFFetcher(
            http_client=AsyncClient(transport=MockTransport(handler=handler)),
            rate_limiter=limiter,
        )

        for _ in range(5):
            await limiter.acquire(credential=credential)

        revision: EntityRevision[Graph] | None = await fetcher.fetch(
            cpf=CPF, credential=credential
        )

        assert revision is not None
        assert calls_at == [0.2]
        assert clock.sleeps == [0.2]
