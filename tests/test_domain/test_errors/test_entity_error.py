from __future__ import annotations

from osint_engine.domain.entities.nodes.company import Company
from osint_engine.domain.errors.entity_error import EntityInvalidIdentifierError

# TESTS


class TestEntityInvalidIdentifierError:
    def test_stores_all_reported_fields(self) -> None:
        error = EntityInvalidIdentifierError(
            subject=Company,
            field="cnpj",
            raw_value="123",
            expected_length=14,
            actual_length=3,
        )

        assert error.subject is Company
        assert error.field == "cnpj"
        assert error.raw_value == "123"
        assert error.expected_length == 14
        assert error.actual_length == 3

    def test_message_reports_subject_field_and_lengths(self) -> None:
        error = EntityInvalidIdentifierError(
            subject=Company,
            field="cnpj",
            raw_value="123",
            expected_length=14,
            actual_length=3,
        )

        message = str(error)

        assert "Company.cnpj" in message
        assert "14" in message
        assert "123" in message
        assert "3" in message
