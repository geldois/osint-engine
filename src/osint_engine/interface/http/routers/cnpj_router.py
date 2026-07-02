from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.routers.handlers.get.get_cnpj import (
    build_get_cnpj_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_cnpj_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)

    router = APIRouter(prefix="/cnpj", dependencies=[Depends(jwt_guard)])

    router.get(path="/{cnpj}")(build_get_cnpj_handler(container=container))

    return router
