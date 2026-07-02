from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from osint_engine.application.auth.user import User


class UserRepository(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find(self, *, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *, username: str) -> User:
        raise NotImplementedError

    @abstractmethod
    async def save(self, *, user: User) -> None:
        raise NotImplementedError
