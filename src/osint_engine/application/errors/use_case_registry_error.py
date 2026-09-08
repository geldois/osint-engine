from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.domain.errors.error_category import ErrorCategory

if TYPE_CHECKING:
    from osint_engine.application.contracts.use_case import UseCase, UseCaseBilling


class UseCaseRegistryError(ApplicationError, error_code=None): ...


class UnregisteredUseCaseError(
    UseCaseRegistryError,
    error_code="USE_CASE_UNREGISTERED",
    category=ErrorCategory.INTERNAL,
):
    subject: type[UseCase[object]]

    @override
    def __init__(self, *, subject: type[UseCase[object]]) -> None:
        super().__init__(subject=subject)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.subject.__name__}' has no billing registration in "
            "UseCaseRegistry — register it with UseCaseRegistry.register(...) "
            "before use."
        )


class DuplicateUseCaseRegistrationError(
    UseCaseRegistryError,
    error_code="USE_CASE_DUPLICATE_REGISTRATION",
    category=ErrorCategory.INTERNAL,
):
    subject: type[UseCase[object]]
    existing: UseCaseBilling

    @override
    def __init__(
        self, *, subject: type[UseCase[object]], existing: UseCaseBilling
    ) -> None:
        super().__init__(subject=subject, existing=existing)

    @override
    def _build_message(self) -> str:
        return f"'{self.subject.__name__}' is already registered as {self.existing!r}"
