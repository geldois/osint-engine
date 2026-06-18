from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.node import Node
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

CnaeID = NewType("CnaeID", UUID)


class Cnae(Node[CnaeID], namespace=EntityNAMESPACE.CNAE):
    code: str

    @override
    def __init__(self, *, code: str) -> None:
        super().__init__(code=code)
