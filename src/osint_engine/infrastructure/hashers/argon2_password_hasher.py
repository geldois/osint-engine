from __future__ import annotations

from typing import override

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from osint_engine.application.contracts.hashers.auth_hasher import AuthHasher

_hasher = PasswordHasher()


class Argon2PasswordHasher(AuthHasher):
    @override
    def hash_(self, *, password: str) -> str:
        return _hasher.hash(password)

    @override
    def verify(self, *, hash_: str, password: str) -> bool:
        try:
            return _hasher.verify(hash=hash_, password=password)
        except (InvalidHashError, VerifyMismatchError):
            return False
