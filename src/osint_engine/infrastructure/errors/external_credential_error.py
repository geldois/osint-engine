from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import Provider


class ExternalCredentialRejectedError(
    InfrastructureError, error_code="EXTERNAL_CREDENTIAL_REJECTED"
):
    username: str
    provider: Provider

    @override
    def __init__(self, *, username: str, provider: Provider) -> None:
        super().__init__(username=username, provider=provider)

    @override
    def _build_message(self) -> str:
        return (
            f"Credential for user '{self.username}' and provider '{self.provider}' "
            f"was rejected by the upstream API."
        )
