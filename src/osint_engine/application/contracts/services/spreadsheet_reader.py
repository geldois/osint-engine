from __future__ import annotations

from typing import Protocol


class ReadSpreadsheetText(Protocol):
    def __call__(self, *, content: bytes, filename: str) -> str: ...
