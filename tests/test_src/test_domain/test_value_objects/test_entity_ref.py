from __future__ import annotations

from uuid import uuid4

import pytest

from osint_engine.domain.errors.entity_error import EntityRefMismatchError
from osint_engine.domain.value_objects.entity_ref import EntityRef
from tests.fakes.domain import FakeMergeableNode, FakeNode


class TestEntityRefConstruction:
    def test_requires_keyword_arguments(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        with pytest.raises(TypeError):
            EntityRef(FakeNode, id_, content_id)  # pyright: ignore[reportCallIssue]

    def test_stores_type_id_and_content_id_by_name(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        ref = EntityRef(entity_type=FakeNode, id=id_, content_id=content_id)

        assert ref.entity_type is FakeNode
        assert ref.id == id_
        assert ref.content_id == content_id


class TestEntityRefEquality:
    def test_two_refs_with_the_same_values_are_equal(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        assert EntityRef(
            entity_type=FakeNode, id=id_, content_id=content_id
        ) == EntityRef(entity_type=FakeNode, id=id_, content_id=content_id)

    def test_swapping_id_and_content_id_produces_a_different_ref(self) -> None:
        first = uuid4()
        second = uuid4()

        assert EntityRef(
            entity_type=FakeNode, id=first, content_id=second
        ) != EntityRef(entity_type=FakeNode, id=second, content_id=first)

    def test_the_entity_type_takes_part_in_equality(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        assert EntityRef(
            entity_type=FakeNode, id=id_, content_id=content_id
        ) != EntityRef(entity_type=FakeMergeableNode, id=id_, content_id=content_id)

    def test_is_frozen(self) -> None:
        ref = EntityRef(entity_type=FakeNode, id=uuid4(), content_id=uuid4())

        with pytest.raises(AttributeError):
            ref.id = uuid4()  # pyright: ignore[reportAttributeAccessIssue]


class TestEntityRefHashing:
    def test_is_hashable(self) -> None:
        ref = EntityRef(entity_type=FakeNode, id=uuid4(), content_id=uuid4())

        assert isinstance(hash(ref), int)

    def test_fits_in_a_frozenset(self) -> None:
        id_ = uuid4()
        content_id = uuid4()

        refs = frozenset(
            {
                EntityRef(entity_type=FakeNode, id=id_, content_id=content_id),
                EntityRef(entity_type=FakeNode, id=id_, content_id=content_id),
            }
        )

        assert len(refs) == 1


class TestEntityRefVerify:
    def test_returns_the_entity_it_points_at(self) -> None:
        node = FakeNode(content="subject")

        assert node.ref.verify(entity=node) is node

    def test_accepts_an_equal_entity_that_is_another_instance(self) -> None:
        node = FakeNode(content="subject")
        twin = FakeNode(content="subject")

        assert node.ref.verify(entity=twin) is twin

    def test_raises_when_the_entity_has_another_id(self) -> None:
        node = FakeNode(content="subject")
        other = FakeNode(content="other")

        with pytest.raises(EntityRefMismatchError):
            node.ref.verify(entity=other)

    def test_raises_when_the_entity_has_another_type(self) -> None:
        node = FakeNode(content="subject")
        ref = EntityRef(
            entity_type=FakeMergeableNode, id=node.id, content_id=node.content_id
        )

        with pytest.raises(EntityRefMismatchError):
            ref.verify(entity=node)

    def test_raises_when_the_entity_has_another_content_id(self) -> None:
        node = FakeNode(content="subject")
        ref = EntityRef(entity_type=FakeNode, id=node.id, content_id=uuid4())

        with pytest.raises(EntityRefMismatchError):
            ref.verify(entity=node)
