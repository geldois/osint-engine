from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from osint_engine.domain.value_objects.entity_ref import EntityRef
from osint_engine.interface.http.presenters.entity_record_presenter import (
    entity_record_to_schema,
)
from osint_engine.interface.http.schemas.entity_record_schema import (
    EntityRecordSchema,
)

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRecord


class TestEntityRecordPresenterFieldMapping:
    def test_maps_every_scalar_field(
        self, make_entity_record: MakeEntityRecord
    ) -> None:
        record = make_entity_record(outcome="expanded")

        result = entity_record_to_schema(record)

        assert isinstance(result, EntityRecordSchema)
        assert result.id == record.id
        assert result.entity_id == record.entity_id
        assert result.outcome == record.outcome
        assert result.provider == record.provider
        assert result.requested_at == record.requested_at
        assert result.username == record.username

    def test_maps_a_present_entity_ref(
        self, make_entity_record: MakeEntityRecord
    ) -> None:
        ref = EntityRef(id=uuid4(), content_id=uuid4())
        record = make_entity_record(outcome="expanded", entity_ref=ref)

        result = entity_record_to_schema(record)

        assert result.entity_ref is not None
        assert result.entity_ref.id == ref.id
        assert result.entity_ref.content_id == ref.content_id

    def test_maps_an_absent_entity_ref_to_none(
        self, make_entity_record: MakeEntityRecord
    ) -> None:
        record = make_entity_record(outcome="empty", entity_ref=None)

        result = entity_record_to_schema(record)

        assert result.entity_ref is None
