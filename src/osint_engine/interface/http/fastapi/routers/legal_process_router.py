from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.application.auth.user import Role
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_role_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_legal_process import (
    build_get_legal_process_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container

_ALLOWED_ROLES = frozenset({Role.ADMIN})


def build_legal_process_router(*, container: Container) -> APIRouter:
    role_guard = build_role_guard(container=container, allowed_roles=_ALLOWED_ROLES)
    rate_limit = build_expansion_rate_limit(scope="legal_process")

    router = APIRouter(
        prefix="/legal-process",
        dependencies=[Depends(role_guard), Depends(rate_limit)],
    )

    router.get(path="/{cpf_or_cnpj:path}", response_model=None)(
        build_get_legal_process_handler(container=container)
    )

    return router
