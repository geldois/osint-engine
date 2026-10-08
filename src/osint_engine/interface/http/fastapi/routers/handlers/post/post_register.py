from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.schemas.register_schema import (  # noqa: TC001
    RegisterSchema,
)
from osint_engine.interface.http.schemas.token_schema import TokenSchema

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_post_register_handler(
    *, container: Container
) -> Callable[[RegisterSchema], Awaitable[TokenSchema]]:
    async def post_register(body: RegisterSchema) -> TokenSchema:
        jwt_service = container.services.jwt_service
        use_case = container.use_cases.register_user(
            username=body.username, password=body.password
        )

        user = await use_case.execute()
        access_token = jwt_service.create_access_token(username=user.username)

        return TokenSchema(access_token=access_token)

    return post_register
