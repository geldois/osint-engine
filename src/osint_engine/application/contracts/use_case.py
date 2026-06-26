from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from typing import final


class UseCase[ReturnType: object](ABC):
    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    @abstractmethod
    async def execute(self) -> ReturnType:
        raise NotImplementedError

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError


class Command(UseCase[None]): ...


class Query[ReturnType: object](UseCase[ReturnType]): ...
