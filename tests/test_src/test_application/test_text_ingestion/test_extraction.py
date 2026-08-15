from __future__ import annotations

from osint_engine.application.text_ingestion.extraction import extract_matches
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.value_objects.text_pattern import TextPatternName

_VALID_CPF = "11144477735"
_VALID_CNPJ = "11222333000181"


class TestExtractMatchesDeterministicIdentifiers:
    def test_finds_a_valid_cpf(self) -> None:
        matches = extract_matches(
            text=f"CPF: {_VALID_CPF}",
            pattern_names=frozenset({TextPatternName.CPF_LABELED}),
        )

        assert len(matches) == 1

        match = next(iter(matches))

        assert match.node_type is Person
        assert dict(match.field_values) == {"cpf": _VALID_CPF}
        assert match.matched_field == "cpf"
        assert match.pattern_name is TextPatternName.CPF_LABELED

    def test_discards_a_cpf_that_fails_checksum(self) -> None:
        matches = extract_matches(
            text="CPF: 00000000000",
            pattern_names=frozenset({TextPatternName.CPF_LABELED}),
        )

        assert matches == frozenset()

    def test_finds_a_valid_cnpj_independently_of_cpf_pattern(self) -> None:
        matches = extract_matches(
            text=f"CNPJ: {_VALID_CNPJ}",
            pattern_names=frozenset(
                {TextPatternName.CPF_LABELED, TextPatternName.CNPJ_LABELED}
            ),
        )

        assert len(matches) == 1

        match = next(iter(matches))

        assert match.node_type is Company
        assert dict(match.field_values) == {"cnpj": _VALID_CNPJ}

    def test_finds_a_composite_cep_and_number_match(self) -> None:
        matches = extract_matches(
            text="Endereco: CEP 01310-100, numero 500",
            pattern_names=frozenset({TextPatternName.CEP_AND_NUMBER}),
        )

        assert len(matches) == 1

        match = next(iter(matches))

        assert match.field_values == (("cep", "01310-100"), ("number", "500"))
        assert match.matched_field == "cep,number"

    def test_one_matching_pattern_is_enough_even_if_others_find_nothing(self) -> None:
        matches = extract_matches(
            text=f"CPF: {_VALID_CPF}",
            pattern_names=frozenset(
                {TextPatternName.CPF_LABELED, TextPatternName.CNPJ_LABELED}
            ),
        )

        assert len(matches) == 1

    def test_returns_empty_when_nothing_in_the_set_matches(self) -> None:
        matches = extract_matches(
            text="nothing relevant here",
            pattern_names=frozenset(
                {TextPatternName.CPF_LABELED, TextPatternName.CNPJ_LABELED}
            ),
        )

        assert matches == frozenset()

    def test_returns_empty_when_no_pattern_name_is_given(self) -> None:
        matches = extract_matches(text=f"CPF: {_VALID_CPF}", pattern_names=frozenset())

        assert matches == frozenset()

    def test_deduplicates_the_same_match_found_twice(self) -> None:
        matches = extract_matches(
            text=f"CPF: {_VALID_CPF} ... again CPF: {_VALID_CPF}",
            pattern_names=frozenset({TextPatternName.CPF_LABELED}),
        )

        assert len(matches) == 1

    def test_two_patterns_matching_the_same_text_produce_two_distinct_matches(
        self,
    ) -> None:
        matches = extract_matches(
            text=f"CPF: {_VALID_CPF}",
            pattern_names=frozenset(
                {TextPatternName.CPF_LOOSE, TextPatternName.CPF_LABELED}
            ),
        )

        assert len(matches) == 2

        found_pattern_names = {match.pattern_name for match in matches}

        assert found_pattern_names == {
            TextPatternName.CPF_LOOSE,
            TextPatternName.CPF_LABELED,
        }
