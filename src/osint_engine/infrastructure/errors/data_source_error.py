from __future__ import annotations

from typing import TYPE_CHECKING, override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError

if TYPE_CHECKING:
    from types import UnionType


def _type_name(subject: type | UnionType) -> str:
    return subject.__name__ if isinstance(subject, type) else str(subject)


class DataSourceError(InfrastructureError, error_code=None): ...


class DataSourceRequestError(DataSourceError, error_code="DATA_SOURCE_REQUEST_FAILED"):
    source: str
    status_code: int | None

    @override
    def __init__(self, *, source: str, status_code: int | None) -> None:
        super().__init__(source=source, status_code=status_code)

    @override
    def _build_message(self) -> str:
        status_code_report = (
            f"with status code {self.status_code}"
            if self.status_code is not None
            else "without a status code"
        )

        return f"'{self.source}' request failed {status_code_report}."


class UnexpectedFieldTypeError(
    DataSourceError, error_code="DATA_SOURCE_UNEXPECTED_FIELD_TYPE"
):
    source: str
    key: str
    expected_type: type | UnionType
    field_type: type

    @override
    def __init__(
        self,
        *,
        source: str,
        key: str,
        expected_type: type | UnionType,
        field_type: type,
    ) -> None:
        super().__init__(
            source=source, key=key, expected_type=expected_type, field_type=field_type
        )

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.source}' returned field '{self.key}' "
            f"with type '{_type_name(self.field_type)}', "
            f"expected '{_type_name(self.expected_type)}'."
        )


class UnexpectedPayloadError(
    DataSourceError, error_code="DATA_SOURCE_UNEXPECTED_PAYLOAD"
):
    source: str
    missing_field: str

    @override
    def __init__(self, *, source: str, missing_field: str) -> None:
        super().__init__(source=source, missing_field=missing_field)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.source}' returned an unexpected payload: "
            f"required field '{self.missing_field}' is missing."
        )
