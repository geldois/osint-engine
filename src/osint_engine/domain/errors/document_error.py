from __future__ import annotations

from typing import override

from osint_engine.domain.errors.domain_error import DomainError


class DocumentError(DomainError, error_code=None): ...


class InvalidMaskedDocumentError(
    DocumentError, error_code="DOCUMENT_INVALID_MASKED_VALUE"
):
    raw_value: str
    expected_length: int
    actual_length: int

    @override
    def __init__(
        self,
        *,
        raw_value: str,
        expected_length: int,
        actual_length: int,
    ) -> None:
        super().__init__(
            raw_value=raw_value,
            expected_length=expected_length,
            actual_length=actual_length,
        )

    @override
    def _build_message(self) -> str:
        return (
            f"Masked document must contain exactly {self.expected_length} "
            f"digits or masks, got '{self.raw_value}' with "
            f"{self.actual_length} structural positions."
        )
