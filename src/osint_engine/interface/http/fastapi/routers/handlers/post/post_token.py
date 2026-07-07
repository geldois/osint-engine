from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm  # noqa: TC002

from osint_engine.interface.http.fastapi.schemas.token_schema import TokenSchema

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_post_token_handler(
    *, container: Container
) -> Callable[[OAuth2PasswordRequestForm], Awaitable[TokenSchema]]:
    async def post_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> TokenSchema:
        jwt_service = container.services.jwt_service
        use_case = container.use_cases.authenticate_user(
            username=form_data.username, password=form_data.password
        )

        user = await use_case.execute()
        access_token = jwt_service.create_access_token(
            username=user.username, role=user.role
        )

        return TokenSchema(access_token=access_token)

    return post_token
