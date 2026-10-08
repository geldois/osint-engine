from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, Response
from fastapi_throttle import RateLimiter

from osint_engine.domain.errors.osint_error import OsintError
from osint_engine.interface.errors.rate_limit_error import RateLimitExceededError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container

_DEFAULT_RETRY_AFTER_SECONDS = 60
_TEN_MINUTES_IN_SECONDS = 10 * 60
_FIFTEEN_MINUTES_IN_SECONDS = 15 * 60
_EXPANSION_REQUESTS_PER_MINUTE = 100
_BATCH_REQUESTS_PER_MINUTE = 10
_REGISTRATIONS_PER_WINDOW = 10
_ANONYMOUS_BUCKET = "anonymous"
_BEARER_SCHEME = "bearer"


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


def build_user_bucket_key(
    *, container: Container, scope: str
) -> Callable[[Request], str]:

    def key(request: Request) -> str:
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")

        if scheme.lower() != _BEARER_SCHEME or not token:
            return f"{scope}:{_ANONYMOUS_BUCKET}"

        try:
            claims = container.services.jwt_service.decode_access_token(token=token)
        except OsintError:
            return f"{scope}:{_ANONYMOUS_BUCKET}"

        return f"{scope}:user:{claims['sub']}"

    return key


def build_auth_token_rate_limit() -> Callable[[Request, Response], Awaitable[None]]:
    return _translate_rate_limit_error(
        RateLimiter(times=5, seconds=_TEN_MINUTES_IN_SECONDS)
    )


def build_register_rate_limit() -> Callable[[Request, Response], Awaitable[None]]:
    return _translate_rate_limit_error(
        RateLimiter(
            times=_REGISTRATIONS_PER_WINDOW, seconds=_FIFTEEN_MINUTES_IN_SECONDS
        )
    )


def build_expansion_rate_limit(
    *, container: Container, scope: str
) -> Callable[[Request, Response], Awaitable[None]]:

    return _translate_rate_limit_error(
        RateLimiter(
            times=_EXPANSION_REQUESTS_PER_MINUTE,
            seconds=60,
            key_func=build_user_bucket_key(
                container=container, scope=f"expansion:{scope}"
            ),
        )
    )


def build_shared_rate_limit(
    *, scope: str
) -> Callable[[Request, Response], Awaitable[None]]:

    return _translate_rate_limit_error(
        RateLimiter(
            times=_EXPANSION_REQUESTS_PER_MINUTE,
            seconds=60,
            key_func=lambda _request: f"expansion:{scope}",
        )
    )


def build_cpf_batch_rate_limit(
    *, container: Container
) -> Callable[[Request, Response], Awaitable[None]]:
    return _translate_rate_limit_error(
        RateLimiter(
            times=_BATCH_REQUESTS_PER_MINUTE,
            seconds=60,
            key_func=build_user_bucket_key(
                container=container, scope="expansion:cpf_batch"
            ),
        )
    )
