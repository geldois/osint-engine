from __future__ import annotations

from typing import override

from osint_engine.application.errors.application_error import ApplicationError


class AuthError(ApplicationError): ...


class InvalidCredentialsAuthError(AuthError):
    username: str

    @override
    def __init__(self, *, username: str) -> None:
        super().__init__(username=username)

    @override
    def _build_message(self) -> str:
        return f"Invalid credentials for user '{self.username}'."
