from dataclasses import FrozenInstanceError
from typing import NewType
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.entity import Edge, Entity
from osint_engine.domain.errors.entity_error import (
    InvalidEntityIDTypeError,
    MissingEntityIdentityContractError,
)

FakeEntityID = NewType("FakeEntityID", UUID)


class FakeEntity(Entity[FakeEntityID]):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)


class FakeFakeEntity:
    def __init__(self) -> None:
        self.id = uuid4()


# VALID CASES


def test_entity_assures_deterministic_content_adressable_id() -> None:
    entity_a = FakeEntity(content="test")
    entity_b = FakeEntity(content="test")

    assert entity_a.id == entity_b.id

    assert entity_a == entity_b

    assert len({entity_a, entity_b}) == 1


def test_entity_preserves_typed_alias_from_injected_id_type() -> None:
    assert FakeEntity.id_type.__name__ == FakeEntityID.__name__

    assert callable(FakeEntity.id_type)

    assert isinstance(FakeEntity.id_type(uuid4()), UUID)


def test_entity_is_hashable_inside_of_data_structures() -> None:
    entity_a = FakeEntity(content="test_a")
    entity_a_copy = FakeEntity(content="test_a")
    entity_b = FakeEntity(content="test_b")
    entities = {entity_a, entity_b}

    assert hash(entity_a) == hash(entity_a_copy)

    assert hash(entity_a) != hash(entity_b)

    assert entity_a in entities

    assert entity_b in entities

    assert len(entities) == 2


def test_edge_declares_primordial_slots() -> None:
    for slot in Edge.__slots__:
        assert slot in ("source_id", "target_id")


# INVALID CASES


def test_entity_raises_when_inherits_from_class_without_id_type() -> None:
    with pytest.raises(MissingEntityIdentityContractError):

        class FakeEntityWithoutIDType(Entity):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)


def test_entity_raises_when_inherits_from_class_with_flat_id_type() -> None:
    with pytest.raises(MissingEntityIdentityContractError):

        class FakeEntityWithFlatIDType(Entity[UUID]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)


def test_entity_raises_when_inherits_from_class_with_non_uuid_id_type() -> None:
    WrongIDType = NewType("WrongIDType", int)

    with pytest.raises(InvalidEntityIDTypeError):

        class FakeEntityWithWrongIDType(Entity[WrongIDType]):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(**kwargs)


def test_entity_raises_on_property_mutation() -> None:
    entity = FakeEntity(content="test")

    with pytest.raises(FrozenInstanceError):
        entity.content = "testing..."

    with pytest.raises(FrozenInstanceError):
        del entity.content


def test_entity_raises_on_comparison_with_diferent_type_object() -> None:
    entity_a = FakeEntity(content="test")
    entity_b = FakeFakeEntity()

    assert entity_a != entity_b
