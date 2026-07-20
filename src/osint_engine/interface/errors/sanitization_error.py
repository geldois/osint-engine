from __future__ import annotations

from typing import override

from osint_engine.interface.errors.interface_error import InterfaceError


class SanitizationError(InterfaceError, error_code=None): ...


class InvalidCNPJError(SanitizationError, error_code="SANITIZATION_INVALID_CNPJ"):
    input_value: str
    digit_count: int

    @override
    def __init__(self, *, input_value: str, digit_count: int) -> None:
        super().__init__(input_value=input_value, digit_count=digit_count)

    @override
    def _build_message(self) -> str:
        return (
            f"CNPJ must contain exactly 14 digits, "
            f"got '{self.input_value}' with {self.digit_count} digits"
        )


class InvalidCPFOrCNPJError(
    SanitizationError, error_code="SANITIZATION_INVALID_CPF_OR_CNPJ"
):
    input_value: str
    digit_count: int

    @override
    def __init__(self, *, input_value: str, digit_count: int) -> None:
        super().__init__(input_value=input_value, digit_count=digit_count)

    @override
    def _build_message(self) -> str:
        return (
            f"CPF or CNPJ must contain exactly 11 or 14 digits, "
            f"got '{self.input_value}' with {self.digit_count} digits"
        )
