from __future__ import annotations

import pytest

from osint_engine.domain.entities.nodes.person import Person
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError


def _make_person(*, cpf: str, name: str = "TARCIANA PAULA GOMES MEDEIROS") -> Person:
    return Person(
        age_range="Entre 41 a 50 anos",
        birthdate=None,
        cpf=cpf,
        name=name,
        registration_date=None,
        registration_status=None,
    )


class TestPersonIdentityNormalization:
    def test_id_differs_for_differently_masked_cpf_with_same_visible_digits(
        self,
    ) -> None:
        formatted = _make_person(cpf="128.734.***-**")
        masked = _make_person(cpf="***128734**")

        assert formatted.id != masked.id

    def test_id_differs_for_genuinely_different_cpf(self) -> None:
        person_a = _make_person(cpf="***128734**")
        person_b = _make_person(cpf="***999999**")

        assert person_a.id != person_b.id

    def test_content_id_differs_for_differently_masked_cpf_with_same_visible_digits(
        self,
    ) -> None:
        formatted = _make_person(cpf="128.734.***-**")
        masked = _make_person(cpf="***128734**")

        assert formatted.content_id != masked.content_id

    def test_id_is_stable_for_the_same_masked_cpf(self) -> None:
        person_a = _make_person(cpf="***128734**")
        person_b = _make_person(cpf="***128734**")

        assert person_a.id == person_b.id
        assert person_a.content_id == person_b.content_id

    def test_id_is_unaffected_by_punctuation_on_unmasked_cpf(self) -> None:
        punctuated = _make_person(cpf="128.734.111-22")
        digits_only = _make_person(cpf="12873411122")

        assert punctuated.id == digits_only.id
        assert punctuated.content_id == digits_only.content_id

    def test_stored_cpf_preserves_original_masking(self) -> None:
        person = _make_person(cpf="***128734**")

        assert person.cpf == "***128734**"


class TestPersonEnrichedFields:
    def test_registration_fields_are_not_part_of_the_identity(self) -> None:
        regular = Person(
            age_range=None,
            birthdate=None,
            cpf="11144477735",
            name=None,
            registration_date="2010-05-20",
            registration_status="REGULAR",
        )
        suspended = Person(
            age_range=None,
            birthdate=None,
            cpf="11144477735",
            name=None,
            registration_date="2019-08-01",
            registration_status="SUSPENSO",
        )

        assert regular.id == suspended.id


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

    def test_raises_when_cpf_contains_a_corrupted_digit(self) -> None:
        with pytest.raises(EntityInvalidIdentifierError) as exc_info:
            _make_person(cpf="123X45678909")

        error = exc_info.value

        assert error.subject is Person
        assert error.field == "cpf"
        assert error.expected_length == 11
        assert error.actual_length == 12
