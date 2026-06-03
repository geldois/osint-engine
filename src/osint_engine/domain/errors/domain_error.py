from __future__ import annotations

from abc import ABC, abstractmethod


class DomainError(ABC, Exception):
    def __init_subclass__(cls, *, error_code: str | None, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls.error_code = error_code

    @abstractmethod
    def __init__(self, *, subject: type) -> None:
        self.subject = subject

        super().__init__(self._build_message())

        if type(self).error_code is None:
            raise MissingErrorIdentityContractError

    @abstractmethod
    def _build_message(self) -> str: ...


class MissingErrorIdentityContractError(
    DomainError, error_code="ERROR_MISSING_IDENTITY_CONTRACT"
):
    def __init__(self) -> None:
        super().__init__(subject=type(self))

    def _build_message(self) -> str:
        base_name = (
            self.subject.__base__.__name__ + ", " if self.subject.__base__ else ""
        )

        return (
            f"'{self.subject.__name__}' identity contract violation - "
            f"pass 'error_code' in: "
            f"{self.subject.__name__}({base_name}error_code='error_code')"
        )
