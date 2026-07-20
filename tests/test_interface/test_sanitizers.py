from __future__ import annotations

import pytest

from osint_engine.interface.errors.sanitization_error import (
    InvalidCNPJError,
    InvalidCPFOrCNPJError,
)
from osint_engine.interface.sanitizers import sanitize_cnpj, sanitize_cpf_or_cnpj


class TestCNPJSanitization:
    def test_sanitize_cnpj_returns_only_digits_from_valid_input(self) -> None:
        cnpj = "11.222.333/0001-81"
        result = sanitize_cnpj(cnpj)

        assert result == "11222333000181"

    def test_sanitize_cnpj_raises_when_digit_count_is_invalid(self) -> None:
        cnpj = "11.222.333/0001"

        with pytest.raises(InvalidCNPJError) as exception:
            sanitize_cnpj(cnpj)

        error = exception.value

        assert error.input_value == cnpj

        assert error.digit_count == 12

        assert "11.222.333/0001" in str(error)

        assert "14 digits" in str(error)


class TestCPFOrCNPJSanitization:
    def test_sanitize_cpf_or_cnpj_returns_only_digits_from_valid_cpf(self) -> None:
        cpf = "111.222.333-81"
        result = sanitize_cpf_or_cnpj(cpf)

        assert result == "11122233381"

    def test_sanitize_cpf_or_cnpj_returns_only_digits_from_valid_cnpj(self) -> None:
        cnpj = "11.222.333/0001-81"
        result = sanitize_cpf_or_cnpj(cnpj)

        assert result == "11222333000181"

    def test_sanitize_cpf_or_cnpj_raises_when_digit_count_is_invalid(self) -> None:
        invalid = "11.222.333-8"

        with pytest.raises(InvalidCPFOrCNPJError) as exception:
            sanitize_cpf_or_cnpj(invalid)

        error = exception.value

        assert error.input_value == invalid

        assert error.digit_count == 9

        assert "11.222.333-8" in str(error)

        assert "11 or 14 digits" in str(error)
