from __future__ import annotations

from typing import override

from osint_engine.application.errors.application_error import ApplicationError


class AuthError(ApplicationError, error_code=None): ...


class InvalidCredentialsError(AuthError, error_code="AUTH_INVALID_CREDENTIALS"):
    username: str

    @override
    def __init__(self, *, username: str) -> None:
        super().__init__(username=username)

    @override
    def _build_message(self) -> str:
        return f"Invalid credentials for user '{self.username}'."
