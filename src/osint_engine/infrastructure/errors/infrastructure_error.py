from __future__ import annotations

from abc import ABC, abstractmethod
from inspect import isabstract
from typing import ClassVar, final

from osint_engine.domain.errors.error_category import ErrorCategory
from osint_engine.domain.errors.osint_error import OsintError


class InfrastructureError(ABC, OsintError):
    error_code: ClassVar[str | None]
    category: ClassVar[ErrorCategory] = ErrorCategory.INTERNAL

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

        if error_code is None and not isabstract(cls):
            message = (
                f"'{cls.__name__}' must declare error_code. "
                f"Pass error_code='CODE' in: "
                f"class {cls.__name__}(..., error_code='CODE')"
            )

            raise TypeError(message)

    @abstractmethod
    def __init__(self, **kwargs: object) -> None:
        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

        super().__init__(self._build_message())

    @abstractmethod
    def _build_message(self) -> str: ...
