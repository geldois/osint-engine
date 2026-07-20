from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.application.auth.external_credential import ExternalCredential
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.schemas.external_credential_schema import (  # noqa: TC001
    ExternalCredentialSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_post_credential_handler(
    *, container: Container
) -> Callable[[ExternalCredentialSchema, dict[str, object]], Awaitable[None]]:
    jwt_guard = build_jwt_guard(container=container)

    async def post_credential(
        body: ExternalCredentialSchema,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> None:
        username = str(payload["sub"])

        credential = ExternalCredential(
            api_key=body.api_key, provider=body.provider, username=username
        )

        use_case = container.use_cases.save_external_credential(credential=credential)

        await use_case.execute()

    return post_credential
