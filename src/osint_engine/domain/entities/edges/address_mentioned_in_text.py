from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.address import AddressID
from osint_engine.domain.entities.nodes.text_source import TextSourceID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.pattern_set_id import PatternSetID  # noqa: TC001

AddressMentionedInTextID = NewType("AddressMentionedInTextID", UUID)


class AddressMentionedInText(
    Edge[AddressMentionedInTextID, AddressID, TextSourceID],
    id_fields=None,
    namespace=EntityNAMESPACE.ADDRESS_TEXT_SOURCE,
):
    matched_field: str
    pattern_id: PatternSetID

    @override
    def __init__(
        self,
        *,
        source_id: AddressID,
        target_id: TextSourceID,
        matched_field: str,
        pattern_id: PatternSetID,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_id=pattern_id,
        )
