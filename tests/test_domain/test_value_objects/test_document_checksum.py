from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from osint_engine.domain.value_objects.document_checksum import (
    is_valid_cnpj_checksum,
    is_valid_cpf_checksum,
)

_VALID_CPF = "11144477735"
_VALID_CNPJ = "11222333000181"


class TestCPFChecksum:
    def test_accepts_a_known_valid_cpf(self) -> None:
        assert is_valid_cpf_checksum(digits=_VALID_CPF)

    def test_rejects_a_cpf_with_a_flipped_final_check_digit(self) -> None:
        flipped = _VALID_CPF[:-1] + str((int(_VALID_CPF[-1]) + 1) % 10)

        assert not is_valid_cpf_checksum(digits=flipped)

    def test_rejects_all_repeated_digits(self) -> None:
        assert not is_valid_cpf_checksum(digits="11111111111")

    def test_rejects_wrong_length(self) -> None:
        assert not is_valid_cpf_checksum(digits=_VALID_CPF[:-1])

    def test_rejects_non_digit_characters(self) -> None:
        assert not is_valid_cpf_checksum(digits="1114447773a")

    @given(st.integers(min_value=0, max_value=8))
    def test_rejects_any_single_flipped_base_digit(self, position: int) -> None:
        original_digit = _VALID_CPF[position]
        flipped_digit = str((int(original_digit) + 1) % 10)
        flipped = _VALID_CPF[:position] + flipped_digit + _VALID_CPF[position + 1 :]

        assert not is_valid_cpf_checksum(digits=flipped)


class TestCNPJChecksum:
    def test_accepts_a_known_valid_cnpj(self) -> None:
        assert is_valid_cnpj_checksum(digits=_VALID_CNPJ)

    def test_rejects_a_cnpj_with_a_flipped_final_check_digit(self) -> None:
        flipped = _VALID_CNPJ[:-1] + str((int(_VALID_CNPJ[-1]) + 1) % 10)

        assert not is_valid_cnpj_checksum(digits=flipped)

    def test_rejects_all_repeated_digits(self) -> None:
        assert not is_valid_cnpj_checksum(digits="11111111111111")

    def test_rejects_wrong_length(self) -> None:
        assert not is_valid_cnpj_checksum(digits=_VALID_CNPJ[:-1])

    def test_rejects_non_digit_characters(self) -> None:
        assert not is_valid_cnpj_checksum(digits="1122233300018a")

    @given(st.integers(min_value=0, max_value=11))
    def test_rejects_any_single_flipped_base_digit(self, position: int) -> None:
        original_digit = _VALID_CNPJ[position]
        flipped_digit = str((int(original_digit) + 1) % 10)
        flipped = _VALID_CNPJ[:position] + flipped_digit + _VALID_CNPJ[position + 1 :]

        assert not is_valid_cnpj_checksum(digits=flipped)
