from __future__ import annotations

from typing import override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError


class AuthError(InfrastructureError): ...


class InvalidTokenAuthError(AuthError):
    detail: str

    @override
    def __init__(self, *, detail: str) -> None:
        super().__init__(detail=detail)

    @override
    def _build_message(self) -> str:
        return self.detail


class NotFoundUserAuthError(AuthError):
    username: str

    @override
    def __init__(self, *, username: str) -> None:
        super().__init__(username=username)

    @override
    def _build_message(self) -> str:
        return f"User '{self.username}' not found."
