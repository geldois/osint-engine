from __future__ import annotations

import pytest

from osint_engine.domain.value_objects.normalization import (
    normalize_address_number,
    normalize_str_to_digits_only,
)


class TestDigitsOnly:
    def test_strips_punctuation_from_formatted_document_number(self) -> None:
        assert normalize_str_to_digits_only(value="33.754.482/0001-24") == "33754482000124"  # noqa: E501

    def test_strips_asterisks_from_masked_document_number(self) -> None:
        assert normalize_str_to_digits_only(value="***128734**") == "128734"

    def test_returns_unchanged_value_when_already_digits_only(self) -> None:
        assert normalize_str_to_digits_only(value="33754482000124") == "33754482000124"

    def test_returns_empty_string_when_value_has_no_digits(self) -> None:
        assert normalize_str_to_digits_only(value="S/N") == ""


class TestNormalizeAddressNumberNumericCanonicalization:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("100", "100"),
            ("0100", "100"),
            ("00100", "100"),
            (" 100 ", "100"),
            ("0", "0"),
            ("000", "0"),
        ],
    )
    def test_strips_leading_zeros_and_surrounding_whitespace(
        self, value: str, expected: str
    ) -> None:
        assert normalize_address_number(value=value) == expected

    def test_equivalent_leading_zero_variants_produce_the_same_value(self) -> None:
        assert normalize_address_number(value="0100") == normalize_address_number(
            value="100"
        )


class TestNormalizeAddressNumberSuffixCanonicalization:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("100A", "100-A"),
            ("100-A", "100-A"),
            ("100/A", "100-A"),
            ("100 A", "100-A"),
            ("100a", "100-A"),
            ("007B", "7-B"),
        ],
    )
    def test_unifies_separators_between_number_and_suffix(
        self, value: str, expected: str
    ) -> None:
        assert normalize_address_number(value=value) == expected

    @pytest.mark.parametrize(
        "variant", ["100A", "100-A", "100/A", "100 A", "100a"]
    )
    def test_equivalent_suffix_variants_produce_the_same_value(
        self, variant: str
    ) -> None:
        assert normalize_address_number(value=variant) == normalize_address_number(
            value="100A"
        )


class TestNormalizeAddressNumberNonNumericFallback:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("LOTE A", "LOTE-A"),
            ("QUADRA-5", "QUADRA-5"),
        ],
    )
    def test_unifies_separators_when_value_has_no_leading_digits(
        self, value: str, expected: str
    ) -> None:
        assert normalize_address_number(value=value) == expected


class TestNormalizeAddressNumberNoNumberCanonicalization:
    @pytest.mark.parametrize(
        "variant",
        ["S/N", "s/n", "SN", "sn", "S/Nº", "s/n°", "sem número", "SEM NUMERO", ""],
    )
    def test_collapses_no_number_variants_to_the_canonical_marker(
        self, variant: str
    ) -> None:
        assert normalize_address_number(value=variant) == "S/N"

    def test_canonical_marker_never_collides_with_a_real_number(self) -> None:
        assert normalize_address_number(value="S/N") != normalize_address_number(
            value="0"
        )


class TestNormalizeAddressNumberIdentityRegression:
    """
    normalize_str_to_digits_only(value="S/N") == "" (see TestDigitsOnly above),
    which collapses every unnumbered address to the same empty identity
    fragment. normalize_address_number exists specifically to close that hole.
    """

    def test_no_number_marker_is_not_the_empty_string(self) -> None:
        assert normalize_address_number(value="S/N") != ""

    def test_blank_input_does_not_collide_with_the_digit_zero(self) -> None:
        assert normalize_address_number(value="") != normalize_address_number(
            value="0"
        )
