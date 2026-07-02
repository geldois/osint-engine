from __future__ import annotations

from typing import Literal, override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError

type CryptContextOperation = Literal["hash", "verify"]


class AuthError(InfrastructureError): ...


class UnexpectedHasherOutputAuthError(AuthError):
    operation: CryptContextOperation
    expected_type: type
    actual_type: type

    @override
    def __init__(
        self,
        *,
        operation: CryptContextOperation,
        expected_type: type,
        actual_type: type,
    ) -> None:
        super().__init__(
            operation=operation, expected_type=expected_type, actual_type=actual_type
        )

    @override
    def _build_message(self) -> str:
        return (
            f"Hasher '{self.operation}' returned '{self.actual_type.__name__}', "
            f"expected '{self.expected_type.__name__}'."
        )


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
