from __future__ import annotations

import re

import pytest

from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.text_pattern_error import FieldPatternGroupMismatchError
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import (
    FieldPattern,
    TextPatternName,
    TextPatternSet,
)

_VALID_CPF_FORMATTED = "111.444.777-35"
_VALID_CPF_BARE = "11144477735"
_INVALID_CPF_FORMATTED = "111.444.777-00"
_INVALID_CPF_BARE = "11144477700"

_VALID_CNPJ_FORMATTED = "11.222.333/0001-81"
_VALID_CNPJ_BARE = "11222333000181"
_INVALID_CNPJ_FORMATTED = "11.222.333/0001-00"
_INVALID_CNPJ_BARE = "11222333000100"


class TestFieldPatternGroupValidation:
    def test_accepts_a_regex_whose_named_groups_match_id_fields_exactly(self) -> None:
        pattern = FieldPattern(node_type=Person, regex=re.compile(r"(?P<cpf>\d{11})"))

        assert pattern.node_type is Person

    def test_accepts_a_composite_regex_matching_a_multi_field_identity(self) -> None:
        pattern = FieldPattern(
            node_type=Address,
            regex=re.compile(r"(?P<cep>\d{8})-(?P<number>\d+)"),
        )

        assert frozenset(pattern.regex.groupindex) == Address.id_fields

    def test_raises_when_a_named_group_is_missing(self) -> None:
        with pytest.raises(FieldPatternGroupMismatchError):
            FieldPattern(node_type=Company, regex=re.compile(r"\d{14}"))

    def test_raises_when_a_named_group_does_not_belong_to_id_fields(self) -> None:
        with pytest.raises(FieldPatternGroupMismatchError):
            FieldPattern(node_type=Person, regex=re.compile(r"(?P<wrong_field>\d{11})"))

    def test_error_reports_expected_and_actual_groups(self) -> None:
        with pytest.raises(FieldPatternGroupMismatchError) as exc_info:
            FieldPattern(node_type=Person, regex=re.compile(r"(?P<wrong_field>\d{11})"))

        error = exc_info.value

        assert error.node_type is Person
        assert error.expected == Person.id_fields
        assert error.actual == frozenset({"wrong_field"})


class TestTextPatternSet:
    def test_holds_its_id_and_patterns(self) -> None:
        pattern_set = TextPatternSet(
            id=PatternSetID("test_set"),
            patterns=frozenset({TextPatternName.CPF_LOOSE}),
        )

        assert pattern_set.id == "test_set"
        assert pattern_set.patterns == frozenset({TextPatternName.CPF_LOOSE})


class TestTextPatternNameMembers:
    @pytest.mark.parametrize("pattern_name", list(TextPatternName))
    def test_every_member_value_is_a_valid_field_pattern(
        self, pattern_name: TextPatternName
    ) -> None:
        assert isinstance(pattern_name.value, FieldPattern)


class TestCPFLoosePattern:
    _REGEX = TextPatternName.CPF_LOOSE.value.regex
    _CHECKS_CPF = staticmethod(
        TextPatternName.CPF_LOOSE.value.checksum_validators["cpf"]
    )

    def test_matches_formatted_cpf_with_valid_checksum(self) -> None:
        match = self._REGEX.search(_VALID_CPF_FORMATTED)

        assert match is not None
        assert self._CHECKS_CPF(match.group("cpf"))

    def test_matches_bare_digits_with_valid_checksum(self) -> None:
        match = self._REGEX.search(_VALID_CPF_BARE)

        assert match is not None
        assert self._CHECKS_CPF(match.group("cpf"))

    def test_checksum_rejects_invalid_formatted_cpf(self) -> None:
        match = self._REGEX.search(_INVALID_CPF_FORMATTED)

        assert match is not None
        assert not self._CHECKS_CPF(match.group("cpf"))

    def test_checksum_rejects_invalid_bare_cpf(self) -> None:
        match = self._REGEX.search(_INVALID_CPF_BARE)

        assert match is not None
        assert not self._CHECKS_CPF(match.group("cpf"))

    def test_does_not_match_empty_string(self) -> None:
        assert self._REGEX.search("") is None

    def test_does_not_match_string_without_digits(self) -> None:
        assert self._REGEX.search("nada aqui") is None

    def test_does_not_capture_eleven_digits_from_inside_a_full_cnpj(self) -> None:
        assert self._REGEX.search(_VALID_CNPJ_BARE) is None


class TestCPFLabeledPattern:
    _REGEX = TextPatternName.CPF_LABELED.value.regex
    _CHECKS_CPF = staticmethod(
        TextPatternName.CPF_LABELED.value.checksum_validators["cpf"]
    )

    def test_matches_bare_digits_with_the_cpf_keyword(self) -> None:
        match = self._REGEX.search(f"CPF: {_VALID_CPF_BARE}")

        assert match is not None
        assert match.group("cpf") == _VALID_CPF_BARE
        assert self._CHECKS_CPF(match.group("cpf"))

    def test_does_not_match_bare_digits_without_the_cpf_keyword(self) -> None:
        assert self._REGEX.search(_VALID_CPF_BARE) is None

    def test_checksum_rejects_invalid_cpf(self) -> None:
        match = self._REGEX.search(f"CPF: {_INVALID_CPF_BARE}")

        assert match is not None
        assert not self._CHECKS_CPF(match.group("cpf"))

    def test_does_not_match_empty_string(self) -> None:
        assert self._REGEX.search("") is None

    def test_does_not_match_string_without_digits(self) -> None:
        assert self._REGEX.search("CPF: nada aqui") is None


class TestCNPJLoosePattern:
    _REGEX = TextPatternName.CNPJ_LOOSE.value.regex
    _CHECKS_CNPJ = staticmethod(
        TextPatternName.CNPJ_LOOSE.value.checksum_validators["cnpj"]
    )

    def test_matches_formatted_cnpj_with_valid_checksum(self) -> None:
        match = self._REGEX.search(_VALID_CNPJ_FORMATTED)

        assert match is not None
        assert self._CHECKS_CNPJ(match.group("cnpj"))

    def test_matches_bare_digits_with_valid_checksum(self) -> None:
        match = self._REGEX.search(_VALID_CNPJ_BARE)

        assert match is not None
        assert self._CHECKS_CNPJ(match.group("cnpj"))

    def test_checksum_rejects_invalid_formatted_cnpj(self) -> None:
        match = self._REGEX.search(_INVALID_CNPJ_FORMATTED)

        assert match is not None
        assert not self._CHECKS_CNPJ(match.group("cnpj"))

    def test_checksum_rejects_invalid_bare_cnpj(self) -> None:
        match = self._REGEX.search(_INVALID_CNPJ_BARE)

        assert match is not None
        assert not self._CHECKS_CNPJ(match.group("cnpj"))

    def test_does_not_match_empty_string(self) -> None:
        assert self._REGEX.search("") is None

    def test_does_not_match_string_without_digits(self) -> None:
        assert self._REGEX.search("nada aqui") is None


class TestCNPJLabeledPattern:
    _REGEX = TextPatternName.CNPJ_LABELED.value.regex
    _CHECKS_CNPJ = staticmethod(
        TextPatternName.CNPJ_LABELED.value.checksum_validators["cnpj"]
    )

    def test_matches_bare_digits_with_the_cnpj_keyword(self) -> None:
        match = self._REGEX.search(f"CNPJ: {_VALID_CNPJ_BARE}")

        assert match is not None
        assert match.group("cnpj") == _VALID_CNPJ_BARE
        assert self._CHECKS_CNPJ(match.group("cnpj"))

    def test_does_not_match_bare_digits_without_the_cnpj_keyword(self) -> None:
        assert self._REGEX.search(_VALID_CNPJ_BARE) is None

    def test_checksum_rejects_invalid_cnpj(self) -> None:
        match = self._REGEX.search(f"CNPJ: {_INVALID_CNPJ_BARE}")

        assert match is not None
        assert not self._CHECKS_CNPJ(match.group("cnpj"))

    def test_does_not_match_empty_string(self) -> None:
        assert self._REGEX.search("") is None

    def test_does_not_match_string_without_digits(self) -> None:
        assert self._REGEX.search("CNPJ: nada aqui") is None


class TestCEPAndNumberPattern:
    _REGEX = TextPatternName.CEP_AND_NUMBER.value.regex

    def test_matches_the_same_sentence_cep_and_number(self) -> None:
        match = self._REGEX.search("Endereco: CEP 01310-100, numero 500")

        assert match is not None
        assert match.group("cep") == "01310-100"
        assert match.group("number") == "500"

    def test_matches_the_nordinal_abbreviation(self) -> None:
        match = self._REGEX.search("Endereco: CEP 01310-100, nº 123")

        assert match is not None
        assert match.group("cep") == "01310-100"
        assert match.group("number") == "123"

    def test_does_not_splice_a_cep_and_number_from_different_sentences(self) -> None:
        text = (
            "O reu mora na CEP 01310-100. Ja a vitima mora na Rua Augusta, numero 250."
        )

        assert self._REGEX.search(text) is None

    def test_does_not_match_empty_string(self) -> None:
        assert self._REGEX.search("") is None

    def test_does_not_match_string_without_digits(self) -> None:
        assert self._REGEX.search("CEP sem numero nenhum") is None
