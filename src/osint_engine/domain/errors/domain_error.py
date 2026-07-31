from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import isabstract
from typing import ClassVar, final, override

from osint_engine.domain.errors.error_category import ErrorCategory
from osint_engine.domain.errors.osint_error import OsintError


def _verify_error_code(*, subject: type[DomainError]) -> None:
    if subject.error_code is None and not isabstract(subject):
        raise MissingErrorIdentityContractError(subject=subject)


class DomainError(ABC, OsintError):
    error_code: ClassVar[str | None]
    category: ClassVar[ErrorCategory] = ErrorCategory.INVALID_INPUT

    @final
    def __init_subclass__(
        cls,
        *,
        error_code: str | None,
        category: ErrorCategory | None = None,
        **kwargs: object,
    ) -> None:
        super().__init_subclass__(**kwargs)

        cls.error_code = error_code

        if category is not None:
            cls.category = category

        _verify_error_code(subject=cls)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

        super().__init__(self._build_message())

    @abstractmethod
    def _build_message(self) -> str: ...


class MissingErrorIdentityContractError(
    DomainError, error_code="ERROR_MISSING_IDENTITY_CONTRACT"
):
    subject: type[DomainError]

    @override
    def __init__(self, *, subject: type[DomainError]) -> None:
        super().__init__(subject=subject)

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
