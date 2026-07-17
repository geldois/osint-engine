from __future__ import annotations

from typing import Literal, NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

SanctionID = NewType("SanctionID", UUID)


class Sanction(
    Node[SanctionID], id_fields=frozenset({"organ"}), namespace=EntityNAMESPACE.SANCTION
):
    organ: Literal["CEIS", "CNEP"]

    @override
    def __init__(self, *, organ: Literal["CEIS", "CNEP"]) -> None:
        super().__init__(
            **{
                key: value
                for key, value in locals().items()
                if key not in {"__class__", "self"}
            }
        )
