from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from math import ceil
from typing import TYPE_CHECKING, override

from osint_engine.application.contracts.services.kipflow_rate_limiter import (
    KipFlowRateLimiter,
)

if TYPE_CHECKING:
    from asyncio import Future
    from collections.abc import Awaitable, Callable

    from osint_engine.application.auth.external_credential import ExternalCredential


@dataclass(frozen=True)
class _Window:
    capacity: float
    rate: float


_WINDOWS = (
    _Window(capacity=5.0, rate=5.0),
    _Window(capacity=100.0, rate=100.0 / 60.0),
    _Window(capacity=1000.0, rate=1000.0 / 3600.0),
)

_TOKEN_EPSILON = 1e-9


@dataclass
class _Bucket:
    tokens: float


@dataclass
class _CredentialState:
    buckets: tuple[_Bucket, ...]
    last_refill: float
    waiters: deque[Future[None]] = field(default_factory=deque)
    wake_task: asyncio.Task[None] | None = None


class InMemoryKipFlowRateLimiter(KipFlowRateLimiter):
    def __init__(
        self,
        *,
        now: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self._now = now
        self._sleep = sleep
        self._lock = asyncio.Lock()
        self._states: dict[str, _CredentialState] = {}

    @override
    async def acquire(self, *, credential: ExternalCredential) -> None:
        key = credential.api_key

        async with self._lock:
            state = self._states.setdefault(key, self._new_state())

            if self._can_take(state):
                self._take(state)

                return

            future = asyncio.get_running_loop().create_future()
            state.waiters.append(future)
            self._arm_pump(key, state)

        await future

    @override
    async def wait_seconds_for(
        self, *, credential: ExternalCredential, count: int
    ) -> int:
        if count <= 0:
            return 0

        async with self._lock:
            state = self._states.setdefault(credential.api_key, self._new_state())
            self._refill(state)

            return self._forecast(state, count=count)

    def _new_state(self) -> _CredentialState:
        now = self._now()

        return _CredentialState(
            buckets=tuple(_Bucket(tokens=window.capacity) for window in _WINDOWS),
            last_refill=now,
        )

    def _refill(self, state: _CredentialState) -> None:
        now = self._now()
        elapsed = now - state.last_refill
        state.last_refill = now

        for bucket, window in zip(state.buckets, _WINDOWS, strict=True):
            bucket.tokens = min(window.capacity, bucket.tokens + elapsed * window.rate)

    def _can_take(self, state: _CredentialState) -> bool:
        return all(bucket.tokens >= 1.0 - _TOKEN_EPSILON for bucket in state.buckets)

    def _take(self, state: _CredentialState) -> None:
        for bucket in state.buckets:
            bucket.tokens -= 1.0

    def _arm_pump(self, key: str, state: _CredentialState) -> None:
        if state.wake_task is not None and not state.wake_task.done():
            return

        state.wake_task = asyncio.get_running_loop().create_task(self._pump(key))

    async def _pump(self, key: str) -> None:
        while True:
            async with self._lock:
                state = self._states[key]
                self._refill(state)

                while state.waiters and self._can_take(state):
                    self._take(state)
                    waiter = state.waiters.popleft()

                    if not waiter.cancelled():
                        waiter.set_result(None)

                if not state.waiters:
                    state.wake_task = None

                    return

                delay = self._head_delay(state)

            await self._sleep(delay)

    def _head_delay(self, state: _CredentialState) -> float:
        return max(
            (1.0 - bucket.tokens) / window.rate if bucket.tokens < 1.0 else 0.0
            for bucket, window in zip(state.buckets, _WINDOWS, strict=True)
        )

    def _forecast(self, state: _CredentialState, *, count: int) -> int:
        demand = len(state.waiters) + count

        return ceil(
            max(
                (demand - bucket.tokens) / window.rate
                if bucket.tokens < demand
                else 0.0
                for bucket, window in zip(state.buckets, _WINDOWS, strict=True)
            )
        )
