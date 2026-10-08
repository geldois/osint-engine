from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.rate_limit import (
    build_cpf_batch_rate_limit,
    build_expansion_rate_limit,
)
from osint_engine.interface.http.fastapi.routers.handlers.get.get_cpf import (
    build_get_cpf_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_cpf_batch import (
    build_post_cpf_batch_estimate_handler,
    build_post_cpf_batch_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_cpf_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)
    rate_limit = build_expansion_rate_limit(container=container, scope="cpf")
    batch_rate_limit = build_cpf_batch_rate_limit(container=container)

    router = APIRouter(prefix="/cpf", dependencies=[Depends(jwt_guard)])

    router.get(path="/{cpf}", response_model=None, dependencies=[Depends(rate_limit)])(
        build_get_cpf_handler(container=container)
    )

    router.post(path="/batch/estimate", dependencies=[Depends(batch_rate_limit)])(
        build_post_cpf_batch_estimate_handler(container=container)
    )

    router.post(path="/batch", dependencies=[Depends(batch_rate_limit)])(
        build_post_cpf_batch_handler(container=container)
    )

    return router
