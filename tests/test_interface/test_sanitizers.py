from __future__ import annotations

import pytest

from osint_engine.interface.errors.sanitization_error import InvalidCNPJError
from osint_engine.interface.sanitizers import sanitize_cnpj


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
