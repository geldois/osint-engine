from __future__ import annotations

import csv
import io
import zipfile
from typing import TYPE_CHECKING
from xml.etree.ElementTree import ParseError

import openpyxl
from openpyxl.utils.exceptions import InvalidFileException

from osint_engine.application.errors.spreadsheet_ingestion_error import (
    FieldTooLargeError,
    FileTooLargeError,
    MalformedSpreadsheetError,
    TooManyRowsError,
    UnsupportedFileTypeError,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

MAX_FILE_BYTES = 10 * 1024 * 1024
_MAX_ROWS_PER_SHEET = 50_000
_ALLOWED_EXTENSIONS = frozenset({"csv", "xlsx"})
_FIELD_LIMIT_ERROR_PREFIX = "field larger than field limit"


def read_spreadsheet_text(*, content: bytes, filename: str) -> str:
    if len(content) > MAX_FILE_BYTES:
        raise FileTooLargeError(max_bytes=MAX_FILE_BYTES, actual_bytes=len(content))

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension == "csv":
        return _read_csv(content=content, filename=filename)
    if extension == "xlsx":
        return _read_xlsx(content=content, filename=filename)

    raise UnsupportedFileTypeError(filename=filename, allowed=_ALLOWED_EXTENSIONS)


def _decode(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")


def _cell_to_text(value: object) -> str:
    return value if isinstance(value, str) else str(value)


def _row_to_line(row: Iterable[object]) -> str:
    return " ".join(_cell_to_text(value) for value in row if value is not None)


def _guard_row_limit(*, index: int, sheet_name: str | None) -> None:
    if index >= _MAX_ROWS_PER_SHEET:
        raise TooManyRowsError(max_rows=_MAX_ROWS_PER_SHEET, sheet_name=sheet_name)


def _read_csv(*, content: bytes, filename: str) -> str:
    decoded = _decode(content)
    reader = csv.reader(io.StringIO(decoded), delimiter=",")
    lines: list[str] = []

    try:
        for index, row in enumerate(reader):
            _guard_row_limit(index=index, sheet_name=None)
            lines.append(_row_to_line(row))
    except TooManyRowsError:
        raise
    except csv.Error as error:
        if str(error).startswith(_FIELD_LIMIT_ERROR_PREFIX):
            raise FieldTooLargeError(
                filename=filename, max_field_bytes=csv.field_size_limit()
            ) from error
        raise MalformedSpreadsheetError(filename=filename) from error
    except Exception as error:
        raise MalformedSpreadsheetError(filename=filename) from error

    return "\n".join(lines)


def _read_xlsx(*, content: bytes, filename: str) -> str:
    try:
        workbook = openpyxl.load_workbook(
            io.BytesIO(content), read_only=True, data_only=True
        )
    except (zipfile.BadZipFile, InvalidFileException, KeyError) as error:
        raise MalformedSpreadsheetError(filename=filename) from error
    except Exception as error:
        raise MalformedSpreadsheetError(filename=filename) from error

    try:
        lines: list[str] = []

        for sheet in workbook.worksheets:
            for index, row in enumerate(sheet.iter_rows(values_only=True)):
                _guard_row_limit(index=index, sheet_name=sheet.title)
                lines.append(_row_to_line(row))

        return "\n".join(lines)
    except TooManyRowsError:
        raise
    except ParseError as error:
        raise MalformedSpreadsheetError(filename=filename) from error
    except Exception as error:
        raise MalformedSpreadsheetError(filename=filename) from error
    finally:
        workbook.close()
