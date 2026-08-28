from __future__ import annotations

from typing import NewType, override
from uuid import UUID

from osint_engine.domain.entities.bases.edge import Edge
from osint_engine.domain.entities.nodes.person import PersonID
from osint_engine.domain.entities.nodes.political_exposure import (
    PoliticalExposureID,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE

PersonHasPoliticalExposureID = NewType("PersonHasPoliticalExposureID", UUID)


class PersonHasPoliticalExposure(
    Edge[PersonHasPoliticalExposureID, PersonID, PoliticalExposureID],
    id_fields=None,
    namespace=EntityNAMESPACE.PERSON_POLITICAL_EXPOSURE,
):
    @override
    def __init__(self, *, source_id: PersonID, target_id: PoliticalExposureID) -> None:
        super().__init__(source_id=source_id, target_id=target_id)
