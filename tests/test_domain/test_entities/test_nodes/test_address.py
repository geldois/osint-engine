from __future__ import annotations

import pytest

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError

# TEST DOUBLES


def _make_address(*, cep: str, number: str = "100") -> Address:
    return Address(
        cep=cep,
        city="BRASILIA",
        complement="ANDAR T I",
        neighborhood="ASA NORTE",
        number=number,
        state="DF",
        street="SAUN QUADRA 5 BLOCO B",
    )


# TESTS


class TestAddressIdentityNormalization:
    def test_id_is_same_for_formatted_and_raw_cep(self) -> None:
        formatted = _make_address(cep="70040-912")
        raw = _make_address(cep="70040912")

        assert formatted.id == raw.id

    def test_id_differs_for_genuinely_different_cep(self) -> None:
        address_a = _make_address(cep="70040912")
        address_b = _make_address(cep="70040913")

        assert address_a.id != address_b.id

    def test_content_id_is_same_for_formatted_and_raw_cep(self) -> None:
        formatted = _make_address(cep="70040-912")
        raw = _make_address(cep="70040912")

        assert formatted.content_id == raw.content_id

    def test_stored_cep_preserves_original_formatting(self) -> None:
        address = _make_address(cep="70040-912")

        assert address.cep == "70040-912"


class TestAddressIdentityValidation:
    def test_raises_when_cep_has_fewer_than_eight_digits(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError):
            _make_address(cep="7004091")

    def test_raises_when_cep_has_more_than_eight_digits(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError):
            _make_address(cep="700409123")

    def test_error_reports_subject_field_and_actual_length(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError) as exc_info:
            _make_address(cep="7004091")

        error = exc_info.value

        assert error.subject is Address
        assert error.field == "cep"
        assert error.expected_length == 8
        assert error.actual_length == 7
