from __future__ import annotations

from typing import override

from osint_engine.domain.errors.entity_error import EntityError
from osint_engine.domain.errors.error_category import ErrorCategory


class TextSourceError(EntityError, error_code=None): ...


class TextSourceEmptyError(
    TextSourceError,
    error_code="TEXT_SOURCE_EMPTY",
    category=ErrorCategory.INVALID_INPUT,
):
    @override
    def __init__(self) -> None:
        super().__init__()

    @override
    def _build_message(self) -> str:
        return "TextSource text must not be empty or whitespace-only."
