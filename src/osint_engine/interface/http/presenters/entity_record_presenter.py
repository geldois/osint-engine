from __future__ import annotations

from typing import TYPE_CHECKING

from osint_engine.interface.http.schemas.entity_record_schema import (
    EntityRecordSchema,
    EntityRefSchema,
)

if TYPE_CHECKING:
    from osint_engine.application.consumption.entity_record import EntityRecord


def entity_record_to_schema(record: EntityRecord, /) -> EntityRecordSchema:
    ref = record.entity_ref
    entity_ref = (
        EntityRefSchema(id=ref.id, content_id=ref.content_id)
        if ref is not None
        else None
    )

    return EntityRecordSchema(
        id=record.id,
        entity_id=record.entity_id,
        entity_ref=entity_ref,
        outcome=record.outcome,
        provider=record.provider,
        requested_at=record.requested_at,
        username=record.username,
    )
