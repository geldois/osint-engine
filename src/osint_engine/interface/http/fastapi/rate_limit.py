from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, Response
from fastapi_throttle import RateLimiter

from osint_engine.interface.errors.rate_limit_error import RateLimitExceededError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_DEFAULT_RETRY_AFTER_SECONDS = 60
_FIFTEEN_MINUTES_IN_SECONDS = 15 * 60
_EXPANSION_REQUESTS_PER_MINUTE = 100


def _translate_rate_limit_error(
    limiter: RateLimiter,
) -> Callable[[Request, Response], Awaitable[None]]:

    async def guarded(request: Request, response: Response) -> None:
        try:
            await limiter(request, response)
        except HTTPException as exception:
            retry_after = _DEFAULT_RETRY_AFTER_SECONDS

            if exception.headers and "Retry-After" in exception.headers:
                retry_after = int(exception.headers["Retry-After"])

            raise RateLimitExceededError(retry_after_seconds=retry_after) from exception

    return guarded


def build_auth_token_rate_limit() -> Callable[[Request, Response], Awaitable[None]]:
    return _translate_rate_limit_error(
        RateLimiter(times=5, seconds=_FIFTEEN_MINUTES_IN_SECONDS)
    )


def build_viewer_token_rate_limit() -> Callable[[Request, Response], Awaitable[None]]:
    return _translate_rate_limit_error(RateLimiter(times=20, seconds=60))


def build_expansion_rate_limit(
    *, scope: str
) -> Callable[[Request, Response], Awaitable[None]]:

    return _translate_rate_limit_error(
        RateLimiter(
            times=_EXPANSION_REQUESTS_PER_MINUTE,
            seconds=60,
            key_func=lambda _request: f"expansion:{scope}",
        )
    )
