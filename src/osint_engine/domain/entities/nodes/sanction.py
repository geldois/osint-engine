from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from decimal import Decimal

SanctionID = NewType("SanctionID", UUID)


class Sanction(
    Node[SanctionID],
    id_fields=frozenset({"organ", "source_id"}),
    namespace=EntityNAMESPACE.SANCTION,
):
    end_date: str | None
    fine_amount: Decimal | None
    legal_basis: tuple[str, ...]
    organ: Literal["CEIS", "CNEP", "CEPIM", "CEAF"]
    process_number: str | None
    publication_date: str | None
    publication_link: str
    sanction_type: str
    sanctioning_body: str
    source_id: str
    start_date: str | None

    @override
    def __init__(
        self,
        *,
        end_date: str | None,
        fine_amount: Decimal | None,
        legal_basis: tuple[str, ...],
        organ: Literal["CEIS", "CNEP", "CEPIM", "CEAF"],
        process_number: str | None,
        publication_date: str | None,
        publication_link: str,
        sanction_type: str,
        sanctioning_body: str,
        source_id: str,
        start_date: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))
