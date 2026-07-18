from __future__ import annotations

from decimal import Decimal

from osint_engine.domain.entities.nodes.sanction import Sanction

# TEST DOUBLES


def _make_sanction(
    *,
    organ: str = "CNEP",
    process_number: str | None = "123/2024",
    fine_amount: Decimal | None = Decimal("1000.50"),
) -> Sanction:
    return Sanction(
        end_date="2025-01-01",
        fine_amount=fine_amount,
        organ=organ,  # pyright: ignore[reportArgumentType]
        process_number=process_number,
        publication_date="2024-01-01",
        sanction_type="Suspensão",
        sanctioning_body="CGU",
        start_date="2024-01-01",
    )


# TESTS


class TestSanctionIdentityComposition:
    def test_id_is_same_for_identical_organ_and_process_number(self) -> None:
        sanction_a = _make_sanction(organ="CNEP", process_number="123/2024")
        sanction_b = _make_sanction(organ="CNEP", process_number="123/2024")

        assert sanction_a.id == sanction_b.id

    def test_id_differs_for_different_process_number_under_the_same_organ(
        self,
    ) -> None:
        sanction_a = _make_sanction(organ="CNEP", process_number="123/2024")
        sanction_b = _make_sanction(organ="CNEP", process_number="456/2024")

        assert sanction_a.id != sanction_b.id

    def test_id_differs_for_the_same_process_number_under_different_organs(
        self,
    ) -> None:
        sanction_a = _make_sanction(organ="CNEP", process_number="123/2024")
        sanction_b = _make_sanction(organ="CEIS", process_number="123/2024")

        assert sanction_a.id != sanction_b.id

    def test_content_id_differs_when_non_identity_fields_change(self) -> None:
        sanction_a = _make_sanction(fine_amount=Decimal("1000.50"))
        sanction_b = _make_sanction(fine_amount=Decimal("2000.00"))

        assert sanction_a.id == sanction_b.id
        assert sanction_a.content_id != sanction_b.content_id


class TestSanctionFieldStorage:
    def test_stores_all_declared_fields(self) -> None:
        sanction = _make_sanction()

        assert sanction.end_date == "2025-01-01"
        assert sanction.fine_amount == Decimal("1000.50")
        assert sanction.organ == "CNEP"
        assert sanction.process_number == "123/2024"
        assert sanction.publication_date == "2024-01-01"
        assert sanction.sanction_type == "Suspensão"
        assert sanction.sanctioning_body == "CGU"
        assert sanction.start_date == "2024-01-01"

    def test_process_number_and_fine_amount_are_optional(self) -> None:
        sanction = _make_sanction(process_number=None, fine_amount=None)

        assert sanction.process_number is None
        assert sanction.fine_amount is None
