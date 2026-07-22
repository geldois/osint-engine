from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from osint_engine.interface.errors.authorization_error import InsufficientRoleError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.application.auth.user import Role
    from osint_engine.config.container import Container

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def build_jwt_guard(
    *, container: Container
) -> Callable[[str], Awaitable[dict[str, object]]]:
    async def jwt_guard(
        token: Annotated[str, Depends(_oauth2_scheme)],
    ) -> dict[str, object]:
        jwt_service = container.services.jwt_service

        return jwt_service.decode_access_token(token=token)

    return jwt_guard


def build_role_guard(
    *, container: Container, allowed_roles: frozenset[Role]
) -> Callable[[str], Awaitable[dict[str, object]]]:
    async def role_guard(
        token: Annotated[str, Depends(_oauth2_scheme)],
    ) -> dict[str, object]:
        jwt_service = container.services.jwt_service
        claims = jwt_service.decode_access_token(token=token)
        role = claims.get("role")

        if role not in allowed_roles:
            raise InsufficientRoleError(
                role=str(role), required_roles=frozenset(str(r) for r in allowed_roles)
            )

        return claims

    return role_guard
