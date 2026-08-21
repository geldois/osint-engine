from __future__ import annotations

import asyncio

import pytest

from osint_engine.application.auth.external_credential import (
    ExternalCredential,
    Provider,
)
from osint_engine.infrastructure.providers.kipflow.in_memory_rate_limiter import (
    InMemoryKipFlowRateLimiter,
)


class _FakeClock:
    def __init__(self, *, auto: bool = True) -> None:
        self._now = 0.0
        self.sleeps: list[float] = []
        self._auto = auto
        self._event = asyncio.Event()

    def now(self) -> float:
        return self._now

    async def sleep(self, delay: float) -> None:
        self.sleeps.append(delay)
        self._now += delay

        if self._auto:
            await asyncio.sleep(0)

            return

        await self._event.wait()

    def release(self) -> None:
        self._event.set()


@pytest.fixture
def clock() -> _FakeClock:
    return _FakeClock()


@pytest.fixture
def limiter(clock: _FakeClock) -> InMemoryKipFlowRateLimiter:
    return InMemoryKipFlowRateLimiter(now=clock.now, sleep=clock.sleep)


def _credential(*, api_key: str) -> ExternalCredential:
    return ExternalCredential(
        api_key=api_key, provider=Provider.KIPFLOW, username="analyst"
    )


def _max_completions_in_window(stamps: list[float], *, window: float) -> int:
    stamps = sorted(stamps)
    best = 0
    left = 0

    for right, moment in enumerate(stamps):
        while stamps[left] <= moment - window:
            left += 1

        best = max(best, right - left + 1)

    return best


class TestInMemoryKipFlowRateLimiter:
    @pytest.mark.asyncio
    async def test_the_sixth_acquire_waits_for_the_second_window_refill(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")

        for _ in range(5):
            await limiter.acquire(credential=credential)

        await limiter.acquire(credential=credential)

        assert clock.sleeps == [0.2]

    @pytest.mark.asyncio
    async def test_the_minute_window_caps_completions_in_any_sixty_seconds(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")
        stamps = await self._drain(
            limiter, clock=clock, credential=credential, count=600
        )

        assert _max_completions_in_window(stamps, window=1.0) <= 10
        assert _max_completions_in_window(stamps, window=60.0) <= 200

    @pytest.mark.asyncio
    async def test_the_hour_window_caps_completions_in_any_hour(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")
        stamps = await self._drain(
            limiter, clock=clock, credential=credential, count=2100
        )

        assert _max_completions_in_window(stamps, window=3600.0) <= 2000

    @pytest.mark.asyncio
    async def test_waiters_complete_in_fifo_order_without_any_dropped(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")

        for _ in range(5):
            await limiter.acquire(credential=credential)

        order: list[int] = []

        async def consume(index: int) -> None:
            await limiter.acquire(credential=credential)
            order.append(index)

        await asyncio.gather(*(consume(index) for index in range(3)))

        assert order == [0, 1, 2]
        assert clock.sleeps == [0.2, 0.2, 0.2]

    @pytest.mark.asyncio
    async def test_distinct_api_keys_never_share_buckets(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        first = _credential(api_key="key-a")
        second = _credential(api_key="key-b")

        for _ in range(5):
            await limiter.acquire(credential=first)

        await limiter.acquire(credential=second)

        assert clock.sleeps == []

    @pytest.mark.asyncio
    async def test_the_same_api_key_shares_one_bucket(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        first = _credential(api_key="key-a")
        second = _credential(api_key="key-a")

        for _ in range(5):
            await limiter.acquire(credential=first)

        await limiter.acquire(credential=second)

        assert clock.sleeps == [0.2]

    @pytest.mark.asyncio
    async def test_a_cancelled_waiter_does_not_strand_the_rest_of_the_queue(
        self, clock: _FakeClock, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")

        for _ in range(5):
            await limiter.acquire(credential=credential)

        head = asyncio.create_task(limiter.acquire(credential=credential))
        tail = asyncio.create_task(limiter.acquire(credential=credential))
        await asyncio.sleep(0)
        head.cancel()
        await asyncio.gather(head, return_exceptions=True)

        await tail

        assert clock.sleeps == [0.2, 0.2]

    @pytest.mark.asyncio
    async def test_forecast_is_zero_only_when_tokens_suffice(
        self, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")

        assert await limiter.wait_seconds_for(credential=credential, count=3) == 0
        assert await limiter.wait_seconds_for(credential=credential, count=50) == 9
        assert await limiter.wait_seconds_for(credential=credential, count=0) == 0
        assert await limiter.wait_seconds_for(credential=credential, count=-4) == 0

    @pytest.mark.asyncio
    async def test_forecast_rounds_up_and_takes_the_binding_window(
        self, limiter: InMemoryKipFlowRateLimiter
    ) -> None:
        credential = _credential(api_key="key-a")

        for _ in range(5):
            await limiter.acquire(credential=credential)

        assert await limiter.wait_seconds_for(credential=credential, count=1) == 1
        assert await limiter.wait_seconds_for(credential=credential, count=100) == 20

        fresh = _credential(api_key="key-b")

        assert await limiter.wait_seconds_for(credential=fresh, count=600) == 300
        assert await limiter.wait_seconds_for(credential=fresh, count=1200) == 720

    @pytest.mark.asyncio
    async def test_forecast_counts_waiters_already_queued_ahead(self) -> None:
        clock = _FakeClock(auto=False)
        limiter = InMemoryKipFlowRateLimiter(now=clock.now, sleep=clock.sleep)
        credential = _credential(api_key="key-a")

        for _ in range(5):
            await limiter.acquire(credential=credential)

        pending = [
            asyncio.create_task(limiter.acquire(credential=credential))
            for _ in range(2)
        ]
        await asyncio.sleep(0)

        assert await limiter.wait_seconds_for(credential=credential, count=100) == 21

        clock.release()
        await asyncio.sleep(0)
        clock.release()
        await asyncio.gather(*pending)

    async def _drain(
        self,
        limiter: InMemoryKipFlowRateLimiter,
        *,
        clock: _FakeClock,
        credential: ExternalCredential,
        count: int,
    ) -> list[float]:
        stamps: list[float] = []

        for _ in range(count):
            await limiter.acquire(credential=credential)
            stamps.append(clock.now())

        return stamps
