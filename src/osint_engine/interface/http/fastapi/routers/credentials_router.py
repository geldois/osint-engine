from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.fastapi.rate_limit import build_expansion_rate_limit
from osint_engine.interface.http.fastapi.routers.handlers.get.get_credentials import (
    build_get_credentials_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.get.get_reveal_credential import (  # noqa: E501
    build_get_reveal_credential_handler,
)
from osint_engine.interface.http.fastapi.routers.handlers.post.post_credential import (
    build_post_credential_handler,
)

if TYPE_CHECKING:
    from osint_engine.config.container import Container


def build_credentials_router(*, container: Container) -> APIRouter:
    jwt_guard = build_jwt_guard(container=container)

    rate_limit = build_expansion_rate_limit(container=container, scope="credentials")

    router = APIRouter(
        prefix="/credentials", dependencies=[Depends(jwt_guard), Depends(rate_limit)]
    )

    router.post(path="", status_code=status.HTTP_204_NO_CONTENT)(
        build_post_credential_handler(container=container)
    )

    router.get(path="")(build_get_credentials_handler(container=container))

    router.get(path="/{provider}/reveal")(
        build_get_reveal_credential_handler(container=container)
    )

    return router
