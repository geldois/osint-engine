from __future__ import annotations

from typing import override

from osint_engine.infrastructure.errors.infrastructure_error import InfrastructureError


class FetcherError(InfrastructureError): ...


class ExternalAPIFetcherError(FetcherError):
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
            else " without a status code"
        )

        return f"'{self.source}' request failed {status_code_report}."


class UnexpectedFieldTypeFetcherError(FetcherError):
    source: str
    key: str
    expected_type: type
    field_type: type

    @override
    def __init__(
        self, *, source: str, key: str, expected_type: type, field_type: type
    ) -> None:
        super().__init__(
            source=source, key=key, expected_type=expected_type, field_type=field_type
        )

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.source}' returned field '{self.key}' "
            f"with type '{self.field_type.__name__}', "
            f"expected '{self.expected_type.__name__}'."
        )


class UnexpectedSchemaFetcherError(FetcherError):
    source: str
    missing_field: str

    @override
    def __init__(self, *, source: str, missing_field: str) -> None:
        super().__init__(source=source, missing_field=missing_field)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.source}' returned an unexpected schema: "
            f"required field '{self.missing_field}' is missing."
        )
