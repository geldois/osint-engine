from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError

if TYPE_CHECKING:
    from osint_engine.application.contracts.uow import UoW


class UoWError(InfrastructureError, error_code=None): ...


class UoWAlreadyPreparedError(UoWError, error_code="UOW_ALREADY_PREPARED"):
    subject: type[UoW]

    @override
    def __init__(self, *, subject: type[UoW]) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' is already prepared. "
            f"Use 'async with' to manage the UoW lifecycle."
        )


class UoWNotPreparedError(UoWError, error_code="UOW_NOT_PREPARED"):
    subject: type[UoW]

    @override
    def __init__(self, *, subject: type[UoW]) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' is not prepared. "
            f"Cannot commit or rollback without preparation."
        )
