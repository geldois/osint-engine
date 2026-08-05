from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.domain.errors.error_category import ErrorCategory
from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError

if TYPE_CHECKING:
    from types import UnionType


def _type_name(subject: type | UnionType) -> str:
    return subject.__name__ if isinstance(subject, type) else str(subject)


class ProviderError(
    InfrastructureError, error_code=None, category=ErrorCategory.UPSTREAM_FAILURE
): ...


class ProviderRequestError(ProviderError, error_code="PROVIDER_REQUEST_FAILED"):
    provider: str
    status_code: int | None

    @override
    def __init__(self, *, provider: str, status_code: int | None) -> None:
        super().__init__(provider=provider, status_code=status_code)

    @override
    def _build_message(self) -> str:
        status_code_report = (
            f"with status code {self.status_code}"
            if self.status_code is not None
            else "without a status code"
        )

        return f"'{self.provider}' request failed {status_code_report}."


class UnexpectedFieldTypeError(
    ProviderError,
    error_code="PROVIDER_UNEXPECTED_FIELD_TYPE",
    category=ErrorCategory.INTERNAL,
):
    provider: str
    key: str
    expected_type: type | UnionType
    field_type: type

    @override
    def __init__(
        self,
        *,
        provider: str,
        key: str,
        expected_type: type | UnionType,
        field_type: type,
    ) -> None:
        super().__init__(
            provider=provider,
            key=key,
            expected_type=expected_type,
            field_type=field_type,
        )

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.provider}' returned field '{self.key}' "
            f"with type '{_type_name(self.field_type)}', "
            f"expected '{_type_name(self.expected_type)}'."
        )


class UnexpectedPayloadError(
    ProviderError,
    error_code="PROVIDER_UNEXPECTED_PAYLOAD",
    category=ErrorCategory.INTERNAL,
):
    provider: str
    missing_field: str

    @override
    def __init__(self, *, provider: str, missing_field: str) -> None:
        super().__init__(provider=provider, missing_field=missing_field)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.provider}' returned an unexpected payload: "
            f"required field '{self.missing_field}' is missing."
        )


class UnexpectedFieldFormatError(
    ProviderError,
    error_code="PROVIDER_UNEXPECTED_FIELD_FORMAT",
    category=ErrorCategory.INTERNAL,
):
    provider: str
    key: str
    raw_value: str
    reason: str

    @override
    def __init__(self, *, provider: str, key: str, raw_value: str, reason: str) -> None:
        super().__init__(provider=provider, key=key, raw_value=raw_value, reason=reason)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.provider}' returned field '{self.key}' "
            f"with value '{self.raw_value}' in an unexpected format: {self.reason}."
        )
