from __future__ import annotations

from abc import ABC, abstractmethod


class AuthHasher(ABC):
    @abstractmethod
    def hash_(self, *, secret: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, *, secret: str, hash_: str) -> bool:
        raise NotImplementedError
