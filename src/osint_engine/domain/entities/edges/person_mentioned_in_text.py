from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.entities.nodes.text_source import TextSourceID
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from osint_engine.domain.value_objects.text_pattern import (
    TextPatternName,
)

PersonMentionedInTextID = NewType("PersonMentionedInTextID", UUID)


class PersonMentionedInText(
    Edge[PersonMentionedInTextID, PersonID, TextSourceID],
    id_fields=frozenset({"pattern_name"}),
    namespace=EntityNAMESPACE.PERSON_TEXT_SOURCE,
):
    matched_field: str
    pattern_name: TextPatternName

    @override
    def __init__(
        self,
        *,
        source_id: PersonID,
        target_id: TextSourceID,
        matched_field: str,
        pattern_name: TextPatternName,
    ) -> None:
        super().__init__(
            source_id=source_id,
            target_id=target_id,
            matched_field=matched_field,
            pattern_name=pattern_name,
        )

    @classmethod
    @override
    def _calculate_id(cls, **kwargs: object) -> PersonMentionedInTextID:
        pattern_name = kwargs.get("pattern_name")

        if isinstance(pattern_name, TextPatternName):
            kwargs["pattern_name"] = pattern_name.name

        return super()._calculate_id(**kwargs)
