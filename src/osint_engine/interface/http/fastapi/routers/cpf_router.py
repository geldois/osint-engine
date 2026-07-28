from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.routers.handlers.get.get_cpf import (
    build_get_cpf_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_cpf_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)

    router = APIRouter(prefix="/cpf", dependencies=[Depends(jwt_guard)])

    router.get(path="/{cpf}")(build_get_cpf_handler(container=container))

    return router
