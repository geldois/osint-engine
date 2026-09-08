from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError, dataclass
from typing import ClassVar, final

from osint_engine.application.errors.use_case_registry_error import (
    DuplicateUseCaseRegistrationError,
    UnregisteredUseCaseError,
)


class UseCase[Return: object](ABC):
    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    @abstractmethod
    async def execute(self) -> Return:
        raise NotImplementedError

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError


class Command(UseCase[None]): ...


class Query[Return: object](UseCase[Return]): ...


@dataclass(eq=True, frozen=True, kw_only=True)
class UseCaseBilling:
    provider: str
    billable: bool


class UseCaseRegistry:
    _REGISTRY: ClassVar[dict[type[UseCase[object]], UseCaseBilling]] = {}

    @classmethod
    def register(
        cls, use_case: type[UseCase[object]], /, *, provider: str, billable: bool
    ) -> None:
        if use_case in cls._REGISTRY:
            raise DuplicateUseCaseRegistrationError(
                subject=use_case, existing=cls._REGISTRY[use_case]
            )

        cls._REGISTRY[use_case] = UseCaseBilling(provider=provider, billable=billable)

    @classmethod
    def billing_for(cls, use_case: type[UseCase[object]], /) -> UseCaseBilling:
        if use_case not in cls._REGISTRY:
            raise UnregisteredUseCaseError(subject=use_case)

        return cls._REGISTRY[use_case]
