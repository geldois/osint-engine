from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.schemas.revision_schema import RevisionSchema

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.application.revision.entity_revision import EntityRevision
    from osint_engine.domain.entities.bases.entity import Entity


def revision_to_schema(revision: EntityRevision[Entity[UUID]], /) -> RevisionSchema:
    return RevisionSchema(
        fetched_at=revision.fetched_at,
        merged_at=revision.merged_at,
        provider=revision.provider,
    )
