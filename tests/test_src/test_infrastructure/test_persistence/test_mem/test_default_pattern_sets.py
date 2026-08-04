from __future__ import annotations

from osint_engine.application.text_ingestion.extraction import extract_matches
from osint_engine.domain.entities.nodes.address import Address
from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.entities.nodes.person import Person
from osint_engine.infrastructure.persistence.mem.default_pattern_sets import (
    BRAZILIAN_DOCUMENT_PATTERNS,
)


class TestCEPAndNumberPattern:
    def test_does_not_splice_a_cep_and_number_from_different_sentences(self) -> None:
        text = (
            "O reu mora na CEP 01310-100. Ja a vitima mora na Rua Augusta, numero 250."
        )

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        assert not any(match.node_type is Address for match in matches)

    def test_matches_the_nordinal_abbreviation(self) -> None:
        text = "Endereco: CEP 01310-100, nº 123"

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        address_match = next(m for m in matches if m.node_type is Address)

        assert dict(address_match.field_values) == {"cep": "01310-100", "number": "123"}

    def test_matches_the_same_sentence_cep_and_number(self) -> None:
        text = "Endereco: CEP 01310-100, numero 500"

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        address_match = next(m for m in matches if m.node_type is Address)

        assert dict(address_match.field_values) == {"cep": "01310-100", "number": "500"}


class TestCPFPattern:
    def test_bare_digits_without_a_cpf_keyword_are_not_extracted(self) -> None:
        text = "Protocolo 11144477735 registrado no sistema."

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        assert not any(match.node_type is Person for match in matches)

    def test_bare_digits_with_a_cpf_keyword_are_extracted(self) -> None:
        text = "CPF: 11144477735"

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        person_match = next(m for m in matches if m.node_type is Person)

        assert dict(person_match.field_values) == {"cpf": "11144477735"}

    def test_formatted_cpf_needs_no_keyword(self) -> None:
        text = "Contato: 111.444.777-35"

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        person_match = next(m for m in matches if m.node_type is Person)

        assert dict(person_match.field_values) == {"cpf": "111.444.777-35"}


class TestCNPJPattern:
    def test_bare_digits_without_a_cnpj_keyword_are_not_extracted(self) -> None:
        text = "Numero de serie 11222333000181 no equipamento."

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        assert not any(match.node_type is Company for match in matches)

    def test_bare_digits_with_a_cnpj_keyword_are_extracted(self) -> None:
        text = "CNPJ: 11222333000181"

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        company_match = next(m for m in matches if m.node_type is Company)

        assert dict(company_match.field_values) == {"cnpj": "11222333000181"}

    def test_formatted_cnpj_needs_no_keyword(self) -> None:
        text = "Empresa 11.222.333/0001-81 registrada"

        matches = extract_matches(text=text, pattern_set=BRAZILIAN_DOCUMENT_PATTERNS)

        company_match = next(m for m in matches if m.node_type is Company)

        assert dict(company_match.field_values) == {"cnpj": "11.222.333/0001-81"}
