from __future__ import annotations

from typing import override

from osint_engine.application.errors.application_error import ApplicationError
from osint_engine.domain.errors.error_category import ErrorCategory


class SpreadsheetIngestionError(ApplicationError, error_code=None): ...


class UnsupportedFileTypeError(
    SpreadsheetIngestionError,
    error_code="SPREADSHEET_INGESTION_UNSUPPORTED_FILE_TYPE",
    category=ErrorCategory.INVALID_INPUT,
):
    filename: str
    allowed: frozenset[str]

    @override
    def __init__(self, *, filename: str, allowed: frozenset[str]) -> None:
        super().__init__(filename=filename, allowed=allowed)

    @override
    def _build_message(self) -> str:
        return (
            f"'{self.filename}' has an unsupported extension, "
            f"expected one of {sorted(self.allowed)}."
        )


class FileTooLargeError(
    SpreadsheetIngestionError,
    error_code="SPREADSHEET_INGESTION_FILE_TOO_LARGE",
    category=ErrorCategory.INVALID_INPUT,
):
    max_bytes: int
    actual_bytes: int

    @override
    def __init__(self, *, max_bytes: int, actual_bytes: int) -> None:
        super().__init__(max_bytes=max_bytes, actual_bytes=actual_bytes)

    @override
    def _build_message(self) -> str:
        return (
            f"File of {self.actual_bytes} bytes exceeds the "
            f"{self.max_bytes}-byte limit."
        )


class TooManyRowsError(
    SpreadsheetIngestionError,
    error_code="SPREADSHEET_INGESTION_TOO_MANY_ROWS",
    category=ErrorCategory.INVALID_INPUT,
):
    max_rows: int
    sheet_name: str | None

    @override
    def __init__(self, *, max_rows: int, sheet_name: str | None) -> None:
        super().__init__(max_rows=max_rows, sheet_name=sheet_name)

    @override
    def _build_message(self) -> str:
        sheet_report = f"'{self.sheet_name}'" if self.sheet_name else "a sheet"

        return f"{sheet_report} exceeds the {self.max_rows}-row limit."


class MalformedSpreadsheetError(
    SpreadsheetIngestionError,
    error_code="SPREADSHEET_INGESTION_MALFORMED",
    category=ErrorCategory.INVALID_INPUT,
):
    filename: str

    @override
    def __init__(self, *, filename: str) -> None:
        super().__init__(filename=filename)

    @override
    def _build_message(self) -> str:
        return f"'{self.filename}' could not be parsed as a valid spreadsheet."
