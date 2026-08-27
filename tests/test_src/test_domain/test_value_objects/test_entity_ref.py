from __future__ import annotations

from uuid import uuid4

import pytest

from osint_engine.domain.value_objects.entity_ref import EntityRef


class TestEntityRefConstruction:
    def test_requires_keyword_arguments(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        with pytest.raises(TypeError):
            EntityRef(id_, content_id)  # pyright: ignore[reportCallIssue]

    def test_stores_id_and_content_id_by_name(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        ref = EntityRef(id=id_, content_id=content_id)

        assert ref.id == id_
        assert ref.content_id == content_id


class TestEntityRefEquality:
    def test_two_refs_with_the_same_values_are_equal(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        assert EntityRef(id=id_, content_id=content_id) == EntityRef(
            id=id_, content_id=content_id
        )

    def test_swapping_id_and_content_id_produces_a_different_ref(self) -> None:
        first = uuid4()
        second = uuid4()

        assert EntityRef(id=first, content_id=second) != EntityRef(
            id=second, content_id=first
        )

    def test_is_frozen(self) -> None:
        ref = EntityRef(id=uuid4(), content_id=uuid4())

        with pytest.raises(AttributeError):
            ref.id = uuid4()  # pyright: ignore[reportAttributeAccessIssue]


class TestEntityRefHashing:
    def test_is_hashable(self) -> None:
        ref = EntityRef(id=uuid4(), content_id=uuid4())

        assert isinstance(hash(ref), int)

    def test_fits_in_a_frozenset(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        refs = frozenset(
            {
                EntityRef(id=id_, content_id=content_id),
                EntityRef(id=id_, content_id=content_id),
            }
        )

        assert len(refs) == 1
