from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.application.auth.user import Role
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_role_guard
from osint_engine.interface.http.fastapi.rate_limit import build_cnpj_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_cnpj import (
    build_get_cnpj_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container

_ALLOWED_ROLES = frozenset({Role.ADMIN, Role.VIEWER})


def build_cnpj_router(*, container: Container) -> APIRouter:
    role_guard = build_role_guard(container=container, allowed_roles=_ALLOWED_ROLES)
    cnpj_rate_limit = build_cnpj_rate_limit(container=container)

    router = APIRouter(
        prefix="/cnpj",
        dependencies=[Depends(role_guard), Depends(cnpj_rate_limit)],
    )

    router.get(path="/{cnpj:path}")(build_get_cnpj_handler(container=container))

    return router
