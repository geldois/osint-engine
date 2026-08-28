from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_pep import (
    build_get_pep_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_pep_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)
    rate_limit = build_expansion_rate_limit(scope="pep")

    router = APIRouter(
        prefix="/peps", dependencies=[Depends(jwt_guard), Depends(rate_limit)]
    )

    router.get(path="/{cpf}", response_model=None)(
        build_get_pep_handler(container=container)
    )

    return router
