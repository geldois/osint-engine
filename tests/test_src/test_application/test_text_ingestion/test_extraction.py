from __future__ import annotations

import re

from osint_engine.application.text_ingestion.extraction import extract_matches
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.value_objects.document_checksum import (
    is_valid_cnpj_checksum,
    is_valid_cpf_checksum,
)
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID
from osint_engine.domain.value_objects.text_pattern import FieldPattern, TextPatternSet

_VALID_CPF = "11144477735"
_VALID_CNPJ = "11222333000181"

_CPF_PATTERN = FieldPattern(
    node_type=Person,
    regex=re.compile(r"(?P<cpf>\d{11})"),
    checksum_validators={"cpf": lambda value: is_valid_cpf_checksum(digits=value)},
)
_CNPJ_PATTERN = FieldPattern(
    node_type=Company,
    regex=re.compile(r"(?P<cnpj>\d{14})"),
    checksum_validators={"cnpj": lambda value: is_valid_cnpj_checksum(digits=value)},
)
_CEP_AND_NUMBER_PATTERN = FieldPattern(
    node_type=Address,
    regex=re.compile(r"(?P<cep>\d{8})-(?P<number>\d+)"),
)


def _pattern_set(*patterns: FieldPattern) -> TextPatternSet:
    return TextPatternSet(id=PatternSetID("test_set"), patterns=patterns)


class TestExtractMatchesDeterministicIdentifiers:
    def test_finds_a_valid_cpf(self) -> None:
        matches = extract_matches(
            text=f"CPF: {_VALID_CPF}", pattern_set=_pattern_set(_CPF_PATTERN)
        )

        assert len(matches) == 1

        match = next(iter(matches))

        assert match.node_type is Person
        assert dict(match.field_values) == {"cpf": _VALID_CPF}
        assert match.matched_field == "cpf"

    def test_discards_a_cpf_that_fails_checksum(self) -> None:
        matches = extract_matches(
            text="CPF: 00000000000", pattern_set=_pattern_set(_CPF_PATTERN)
        )

        assert matches == frozenset()

    def test_finds_a_valid_cnpj_independently_of_cpf_pattern(self) -> None:
        matches = extract_matches(
            text=f"CNPJ: {_VALID_CNPJ}",
            pattern_set=_pattern_set(_CPF_PATTERN, _CNPJ_PATTERN),
        )

        assert len(matches) == 1

        match = next(iter(matches))

        assert match.node_type is Company
        assert dict(match.field_values) == {"cnpj": _VALID_CNPJ}

    def test_finds_a_composite_cep_and_number_match(self) -> None:
        matches = extract_matches(
            text="Endereco: 01310100-500",
            pattern_set=_pattern_set(_CEP_AND_NUMBER_PATTERN),
        )

        assert len(matches) == 1

        match = next(iter(matches))

        assert match.node_type is Address
        assert dict(match.field_values) == {"cep": "01310100", "number": "500"}
        assert match.matched_field == "cep,number"

    def test_one_matching_pattern_is_enough_even_if_others_find_nothing(self) -> None:

        matches = extract_matches(
            text=f"CPF: {_VALID_CPF}",
            pattern_set=_pattern_set(_CPF_PATTERN, _CNPJ_PATTERN),
        )

        assert len(matches) == 1

    def test_returns_empty_when_nothing_in_the_set_matches(self) -> None:
        matches = extract_matches(
            text="nothing relevant here",
            pattern_set=_pattern_set(_CPF_PATTERN, _CNPJ_PATTERN),
        )

        assert matches == frozenset()

    def test_deduplicates_the_same_match_found_twice(self) -> None:
        matches = extract_matches(
            text=f"{_VALID_CPF} ... again {_VALID_CPF}",
            pattern_set=_pattern_set(_CPF_PATTERN),
        )

        assert len(matches) == 1
