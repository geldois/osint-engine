from __future__ import annotations

from typing import TYPE_CHECKING, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.entity import own_init_kwargs
from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

if TYPE_CHECKING:
    from decimal import Decimal

LegalProcessID = NewType("LegalProcessID", UUID)


class LegalProcess(
    Node[LegalProcessID],
    id_fields=frozenset({"process_number"}),
    namespace=EntityNAMESPACE.LEGAL_PROCESS,
):
    court: str | None
    current_status: str | None
    distribution_date: str | None
    execution_value: Decimal | None
    is_secret_of_justice: bool | None
    lawsuit_value: Decimal | None
    lawsuit_value_currency: str | None
    process_class: str | None
    process_number: str
    process_url: str | None
    state: str | None

    @override
    def __init__(
        self,
        *,
        court: str | None,
        current_status: str | None,
        distribution_date: str | None,
        execution_value: Decimal | None,
        is_secret_of_justice: bool | None,
        lawsuit_value: Decimal | None,
        lawsuit_value_currency: str | None,
        process_class: str | None,
        process_number: str,
        process_url: str | None,
        state: str | None,
    ) -> None:
        super().__init__(**own_init_kwargs(**locals()))
