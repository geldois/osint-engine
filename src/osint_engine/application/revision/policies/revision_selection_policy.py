from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from osint_engine.application.errors.revision_error import EmptyRevisionSelectionError
from osint_engine.domain.entities.entity import Entity

if TYPE_CHECKING:
    from collections.abc import Iterable

    from osint_engine.application.revision.entity_revision import EntityRevision


class RevisionSelectionPolicy(Protocol):
    def __call__[Entity_: Entity[UUID]](
        self, entity_revisions: Iterable[EntityRevision[Entity_]], /
    ) -> EntityRevision[Entity_]: ...


def select_current_by_newest_fetched[Entity_: Entity[UUID]](
    entity_revisions: Iterable[EntityRevision[Entity_]], /
) -> EntityRevision[Entity_]:
    """
    Picks the revision with the highest fetched_at; merged_at only breaks ties
    where fetched_at is equal, favoring a merge-derived revision over a raw fetch.
    """

    current = max(
        entity_revisions,
        key=lambda revision: (
            revision.fetched_at,
            revision.merged_at is not None,
            revision.merged_at or revision.fetched_at,
        ),
        default=None,
    )

    if current is None:
        raise EmptyRevisionSelectionError

    return current
