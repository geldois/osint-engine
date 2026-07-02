from __future__ import annotations

from typing import override

from passlib.context import CryptContext

from osint_engine.application.contracts.hashers.auth_hasher import AuthHasher
from osint_engine.infrastructure.errors.auth_error import (
    UnexpectedHasherOutputAuthError,
)

_crypt_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordHasher(AuthHasher):
    @override
    def hash_(self, *, secret: str) -> str:
        hashed = _crypt_context.hash(secret=secret)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

        if not isinstance(hashed, str):
            raise UnexpectedHasherOutputAuthError(
                operation="hash",
                expected_type=str,
                actual_type=type(hashed),  # pyright: ignore[reportUnknownArgumentType]
            )

        return hashed

    @override
    def verify(self, *, secret: str, hash_: str) -> bool:
        result = _crypt_context.verify(secret=secret, hash=hash_)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]

        if not isinstance(result, bool):
            raise UnexpectedHasherOutputAuthError(
                operation="verify",
                expected_type=bool,
                actual_type=type(result),  # pyright: ignore[reportUnknownArgumentType]
            )

        return result
