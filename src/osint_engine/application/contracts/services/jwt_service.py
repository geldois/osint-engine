from __future__ import annotations

from abc import ABC, abstractmethod


class JWTService(ABC):
    @abstractmethod
    def create_access_token(self, *, username: str, role: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_access_token(self, *, token: str) -> dict[str, object]:
        raise NotImplementedError
