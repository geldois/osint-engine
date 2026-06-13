from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from inspect import isabstract
from typing import final, override


def _verify_error_code(*, subject: type[DomainError]) -> None:
    if subject.error_code is None and not isabstract(subject):
        raise MissingErrorIdentityContractError


class DomainError(ABC, Exception):
    @final
    def __init_subclass__(cls, *, error_code: str | None, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls.error_code = error_code

        _verify_error_code(subject=cls)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

        super().__init__(self._build_message())

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError

    @abstractmethod
    def _build_message(self) -> str: ...


class MissingErrorIdentityContractError(
    DomainError, error_code="ERROR_MISSING_IDENTITY_CONTRACT"
):
    subject: type[DomainError]

    @override
    def __init__(self) -> None:
        super().__init__(subject=type(self))

    @override
    def _build_message(self) -> str:
        base_name = (
            self.subject.__base__.__name__ + ", " if self.subject.__base__ else ""
        )

        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'error_code' in: "
            f"{self.subject.__name__}({base_name}error_code='error_code')"
        )
