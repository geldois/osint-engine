from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from osint_engine.application.auth.user import Role
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_role_guard
from osint_engine.interface.http.fastapi.routers.handlers.post.post_credential import (
    build_post_credential_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container

_ALLOWED_ROLES = frozenset({Role.ADMIN})


def build_credentials_router(*, container: Container) -> APIRouter:
    role_guard = build_role_guard(container=container, allowed_roles=_ALLOWED_ROLES)

    router = APIRouter(prefix="/credentials", dependencies=[Depends(role_guard)])

    router.post(path="", status_code=status.HTTP_204_NO_CONTENT)(
        build_post_credential_handler(container=container)
    )

    return router
