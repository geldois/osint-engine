from __future__ import annotations

from osint_engine.domain.value_objects.normalization import digits_only


class TestDigitsOnly:
    def test_strips_punctuation_from_formatted_document_number(self) -> None:
        assert digits_only(value="33.754.482/0001-24") == "33754482000124"

    def test_strips_asterisks_from_masked_document_number(self) -> None:
        assert digits_only(value="***128734**") == "128734"

    def test_returns_unchanged_value_when_already_digits_only(self) -> None:
        assert digits_only(value="33754482000124") == "33754482000124"

    def test_returns_empty_string_when_value_has_no_digits(self) -> None:
        assert digits_only(value="S/N") == ""
