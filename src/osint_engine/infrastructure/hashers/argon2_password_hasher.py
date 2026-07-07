from __future__ import annotations

from typing import override

from argon2 import PasswordHasher as _Argon2Hasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from osint_engine.application.contracts.hashers.password_hasher import PasswordHasher

_hasher = _Argon2Hasher()


class Argon2PasswordHasher(PasswordHasher):
    @override
    def hash_(self, *, password: str) -> str:
        return _hasher.hash(password)

    @override
    def verify(self, *, hash_: str, password: str) -> bool:
        try:
            return _hasher.verify(hash=hash_, password=password)
        except (InvalidHashError, VerifyMismatchError):
            return False
