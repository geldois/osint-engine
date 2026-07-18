from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from decimal import Decimal

SanctionID = NewType("SanctionID", UUID)


class Sanction(
    Node[SanctionID],
    id_fields=frozenset({"organ", "process_number"}),
    namespace=EntityNAMESPACE.SANCTION,
):
    end_date: str | None
    fine_amount: Decimal | None
    organ: Literal["CEIS", "CNEP"]
    process_number: str | None
    publication_date: str | None
    sanction_type: str
    sanctioning_body: str
    start_date: str | None

    @override
    def __init__(
        self,
        *,
        end_date: str | None,
        fine_amount: Decimal | None,
        organ: Literal["CEIS", "CNEP"],
        process_number: str | None,
        publication_date: str | None,
        sanction_type: str,
        sanctioning_body: str,
        start_date: str | None,
    ) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )
