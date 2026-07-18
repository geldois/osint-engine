from __future__ import annotations

import pytest

from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError

# TEST DOUBLES


def _make_person(*, cpf: str, name: str = "TARCIANA PAULA GOMES MEDEIROS") -> Person:
    return Person(age_range="Entre 41 a 50 anos", cpf=cpf, name=name)


# TESTS


class TestPersonIdentityNormalization:
    def test_id_is_same_for_formatted_and_raw_cpf(self) -> None:
        formatted = _make_person(cpf="128.734.***-**")
        masked = _make_person(cpf="***128734**")

        assert formatted.id == masked.id

    def test_id_differs_for_genuinely_different_cpf(self) -> None:
        person_a = _make_person(cpf="***128734**")
        person_b = _make_person(cpf="***999999**")

        assert person_a.id != person_b.id

    def test_content_id_is_same_for_formatted_and_raw_cpf(self) -> None:
        formatted = _make_person(cpf="128.734.***-**")
        masked = _make_person(cpf="***128734**")

        assert formatted.content_id == masked.content_id

    def test_stored_cpf_preserves_original_masking(self) -> None:
        person = _make_person(cpf="***128734**")

        assert person.cpf == "***128734**"


class TestPersonIdentityValidation:
    def test_raises_when_masked_cpf_has_fewer_than_eleven_characters(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError):
            _make_person(cpf="***128734*")

    def test_raises_when_masked_cpf_has_more_than_eleven_characters(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError):
            _make_person(cpf="***128734***")

    def test_raises_when_unmasked_cpf_has_fewer_than_eleven_digits(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError):
            _make_person(cpf="1287346")

    def test_error_reports_subject_field_and_actual_length(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError) as exc_info:
            _make_person(cpf="1287346")

        error = exc_info.value

        assert error.subject is Person
        assert error.field == "cpf"
        assert error.expected_length == 11
        assert error.actual_length == 7
