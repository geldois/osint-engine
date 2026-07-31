from decimal import Decimal
from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PossiblyMatchesID = NewType("PossiblyMatchesID", UUID)


class PossiblyMatches[NodeID: UUID](
    Edge[PossiblyMatchesID, NodeID, NodeID],
    id_fields=None,
    namespace=EntityNAMESPACE.POSSIBLY_MATCHES,
):
    confidence: Decimal

    @override
    def __init__(
        self, *, source_id: NodeID, target_id: NodeID, confidence: Decimal
    ) -> None:
        if source_id > target_id:
            source_id, target_id = target_id, source_id

        super().__init__(
            source_id=source_id, target_id=target_id, confidence=confidence
        )
