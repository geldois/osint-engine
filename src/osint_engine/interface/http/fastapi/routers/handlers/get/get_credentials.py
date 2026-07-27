from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends

from osint_engine.application.auth.external_credential import Provider
from osint_engine.interface.http.fastapi.dependencies.jwt_guard import build_jwt_guard
from osint_engine.interface.http.schemas.external_credential_schema import (
    ExternalCredentialStatusSchema,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from osint_engine.config.container import Container


def build_get_credentials_handler(
    *, container: Container
) -> Callable[
    [dict[str, object]], Awaitable[list[ExternalCredentialStatusSchema]]
]:
    jwt_guard = build_jwt_guard(container=container)

    async def get_credentials(
        payload: dict[str, object] = Depends(jwt_guard),  # noqa: B008
    ) -> list[ExternalCredentialStatusSchema]:
        username = str(payload["sub"])

        use_case = container.use_cases.list_external_credentials(username=username)

        configured_providers = await use_case.execute()

        return [
            ExternalCredentialStatusSchema(
                configured=provider in configured_providers, provider=provider
            )
            for provider in Provider
        ]

    return get_credentials
