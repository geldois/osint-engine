from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.application.auth.external_credential import Provider  # noqa: TC001
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.schemas.external_credential_schema import (
    ExternalCredentialRevealSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_reveal_credential_handler(
    *, container: Container
) -> Callable[[Provider, dict[str, object]], Awaitable[ExternalCredentialRevealSchema]]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_reveal_credential(
        provider: Provider,
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> ExternalCredentialRevealSchema:
        username = str(payload["sub"])

        use_case = container.use_cases.reveal_external_credential(
            provider=provider, username=username
        )

        api_key = await use_case.execute()

        return ExternalCredentialRevealSchema(api_key=api_key)

    return get_reveal_credential
