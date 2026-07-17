from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from osint_engine.application.errors.revision_error import EntityIDMismatchError
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.entity import Entity


class RevisionMergePolicy(Protocol):
    def __call__[Entity_: Entity[UUID]](
        self, left: EntityRevision[Entity_], right: EntityRevision[Entity_], /
    ) -> EntityRevision[Entity_]: ...


def merge_by_filled_fields_policy[Entity_: Entity[UUID]](
    left: EntityRevision[Entity_], right: EntityRevision[Entity_], /
) -> EntityRevision[Entity_]:
    """
    Reconciles two revisions of the same entity: the most recent (by fetched_at)
    wins on every non-null field; the older revision only fills fields left null
    by the newer one. Identical content_id short-circuits to the newer revision.
    """

    if left.entity.id != right.entity.id:
        raise EntityIDMismatchError(left_id=left.entity.id, right_id=right.entity.id)

    oldest = left if left.fetched_at < right.fetched_at else right
    newest = right if oldest is left else left

    if left.entity.content_id == right.entity.content_id:
        return newest

    fills: dict[str, object] = {
        field: getattr(oldest.entity, field)
        for field, value in newest.entity.reconstruct_kwargs().items()
        if value is None
    }

    return EntityRevision(
        entity=newest.entity.evolve(**fills),
        fetched_at=newest.fetched_at,
        merged_at=datetime.now(tz=UTC),
    )
