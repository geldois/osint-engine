from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, Response
from fastapi_throttle import RateLimiter

from osint_engine.application.auth.user import Role
from osint_engine.infrastructure.errors.token_error import TokenError
from osint_engine.interface.errors.rate_limit_error import RateLimitExceededError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container

_DEFAULT_RETRY_AFTER_SECONDS = 60
_FIFTEEN_MINUTES_IN_SECONDS = 15 * 60


def _decode_role(request: Request, *, container: Container) -> str | None:
    auth_header = request.headers.get("authorization", "")

    if not auth_header.lower().startswith("bearer "):
        return None

    token = auth_header.removeprefix("Bearer ").removeprefix("bearer ")

    try:
        claims = container.services.jwt_service.decode_access_token(token=token)
    except TokenError:
        return None

    role = claims.get("role")

    return role if isinstance(role, str) else None


def _translate_rate_limit_error(
    limiter: RateLimiter,
) -> Callable[[Request, Response], Awaitable[None]]:
    """fastapi-throttle raises a bare HTTPException; wrapping it keeps every
    error response on the app's own ErrorSchema/correlation_id shape
    instead of the library's own untagged {"detail": ...} body."""

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


def build_cnpj_rate_limit(
    *, container: Container
) -> Callable[[Request, Response], Awaitable[None]]:
    """Every CNPJ lookup proxies to the upstream BrasilAPI, whose own
    per-minute quota is undocumented and shared across all callers of this
    deployment (they all originate from this server's IP). The per-role
    buckets alone can sum past that shared quota under concurrent load, so a
    global bucket caps the combined outbound rate regardless of role split."""

    admin_limit = _translate_rate_limit_error(
        RateLimiter(times=60, seconds=60, key_func=lambda _request: "cnpj:ADMIN")
    )
    viewer_limit = _translate_rate_limit_error(
        RateLimiter(times=5, seconds=60, key_func=lambda _request: "cnpj:VIEWER")
    )
    global_limit = _translate_rate_limit_error(
        RateLimiter(times=30, seconds=60, key_func=lambda _request: "cnpj:GLOBAL")
    )

    async def cnpj_rate_limit(request: Request, response: Response) -> None:
        role = _decode_role(request, container=container)

        if role == Role.ADMIN:
            await admin_limit(request, response)
        else:
            await viewer_limit(request, response)

        await global_limit(request, response)

    return cnpj_rate_limit
