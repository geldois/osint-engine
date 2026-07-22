from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.application.auth.user import Role
from osint_engine.interface.http.schemas.token_schema import TokenSchema

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container

_VIEWER_USERNAME = "visitor"


def build_post_viewer_token_handler(
    *, container: Container
) -> Callable[[], Awaitable[TokenSchema]]:
    async def post_viewer_token() -> TokenSchema:
        jwt_service = container.services.jwt_service
        access_token = jwt_service.create_access_token(
            username=_VIEWER_USERNAME,
            role=Role.VIEWER,
            expire_minutes=container.settings.viewer_token_expire_minutes,
        )

        return TokenSchema(access_token=access_token)

    return post_viewer_token
