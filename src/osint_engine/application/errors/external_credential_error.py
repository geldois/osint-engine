from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.errors.application_error import ApplicationError

if TYPE_CHECKING:
    from osint_engine.application.auth.external_credential import Provider


class ExternalCredentialError(ApplicationError, error_code=None): ...


class ExternalCredentialNotFoundError(
    ExternalCredentialError, error_code="EXTERNAL_CREDENTIAL_NOT_FOUND"
):
    username: str
    provider: Provider

    @override
    def __init__(self, *, username: str, provider: Provider) -> None:
        super().__init__(username=username, provider=provider)

    @override
    def _build_message(self) -> str:
        return (
            f"No credential found for user '{self.username}' "
            f"and provider '{self.provider}'."
        )
