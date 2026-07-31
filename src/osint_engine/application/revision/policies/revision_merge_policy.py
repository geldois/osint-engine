from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from osint_engine.application.errors.revision_error import EntityIDMismatchError
from osint_engine.application.revision.entity_revision import EntityRevision
from osint_engine.domain.entities.bases.entity import Entity


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

    newest_kwargs = newest.entity.reconstruct_kwargs()
    fills: dict[str, object] = {
        field: getattr(oldest.entity, field)
        for field, value in newest_kwargs.items()
        if value is None
    }

    # `newest` contributed nothing of its own (every non-identity field it
    # carries was null and got backfilled from `oldest`) — attribute the
    # merged result to where its actual content came from, not to whichever
    # side merely happened to be fetched more recently. Identity fields are
    # excluded since they're never null and would otherwise always block
    # this from ever being true.
    non_identity_fields = newest_kwargs.keys() - newest.entity.id_fields
    newest_contributed_nothing = bool(non_identity_fields) and non_identity_fields <= (
        fills.keys()
    )
    source = oldest.source if newest_contributed_nothing else newest.source

    return EntityRevision(
        entity=newest.entity.evolve(**fills),
        fetched_at=newest.fetched_at,
        merged_at=datetime.now(tz=UTC),
        source=source,
    )
