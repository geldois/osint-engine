from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash_(self, *, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, *, hash_: str | None, password: str) -> bool:
        raise NotImplementedError
