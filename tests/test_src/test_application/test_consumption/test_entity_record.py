from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from osint_engine.application.consumption.entity_record import EntityRecord
from osint_engine.domain.value_objects.entity_ref import EntityRef

if TYPE_CHECKING:
    from tests.conftest import MakeEntityRecord


class TestEntityRecordConstruction:
    def test_requires_keyword_arguments(self) -> None:
        args: tuple[object, ...] = (
            uuid4(),
            uuid4(),
            None,
            "expanded",
            "kipflow",
            None,
            "alice",
        )

        with pytest.raises(TypeError):
            EntityRecord(*args)  # pyright: ignore[reportCallIssue]

    def test_entity_ref_defaults_are_never_implicit(
        self, make_entity_record: MakeEntityRecord
    ) -> None:
        expanded = make_entity_record(
            outcome="expanded", entity_ref=EntityRef(id=uuid4(), content_id=uuid4())
        )
        empty = make_entity_record(outcome="empty", entity_ref=None)

        assert expanded.entity_ref is not None
        assert empty.entity_ref is None


class TestEntityRecordImmutability:
    def test_cannot_be_rebound(self, make_entity_record: MakeEntityRecord) -> None:
        record = make_entity_record()

        with pytest.raises(FrozenInstanceError):
            record.outcome = "failed"  # pyright: ignore[reportAttributeAccessIssue]


class TestEntityRecordIdentity:
    def test_two_records_for_the_same_attempt_get_distinct_ids(
        self, make_entity_record: MakeEntityRecord
    ) -> None:
        entity_id = uuid4()

        first = make_entity_record(entity_id=entity_id)
        second = make_entity_record(entity_id=entity_id)

        assert first.id != second.id
