from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import NewType
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.entity_error import (
    InvalidEntityIDTypeError,
    MissingEntityIDTypeError,
)
from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE
from tests.fakes import FakeEntity, FakeEntityID


class FakeEntityWithDiffNAMESPACE(
    Entity[FakeEntityID], namespace=EntityNAMESPACE.TEST_DIFF
):
    content: str

    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(identity_fields=None, content=content, **kwargs)


class FakeFakeEntity:
    def __init__(self, *, content: str) -> None:
        self.id = uuid4()
        self.content = content


# VALID CASES


def test_entity_assures_deterministic_content_adressable_id() -> None:
    entity_a = FakeEntity(content="test")
    entity_b = FakeEntity(content="test")

    assert entity_a.id == entity_b.id

    assert entity_a == entity_b

    assert len({entity_a, entity_b}) == 1

    assert entity_a is not entity_b


def test_entity_returns_false_on_comparison_when_namespaces_are_different() -> None:
    entity_a = FakeEntity(content="test")
    entity_b = FakeEntityWithDiffNAMESPACE(content="test")

    assert entity_a.id != entity_b.id

    assert entity_a != entity_b

    assert len({entity_a, entity_b}) == 2


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


def test_entity_returns_false_on_comparison_with_diferent_type_object() -> None:
    entity_a = FakeEntity(content="test")
    entity_b = FakeFakeEntity(content="test")

    assert entity_a != entity_b


# INVALID CASES


def test_entity_raises_when_inherits_from_class_without_id_type() -> None:
    with pytest.raises(MissingEntityIDTypeError):

        class FakeEntityWithoutIDType(Entity, namespace=EntityNAMESPACE.TEST):  # pyright: ignore[reportUnusedClass, reportMissingTypeArgument]
            def __init__(self, **kwargs: object) -> None:
                super().__init__(identity_fields=None, **kwargs)


def test_entity_raises_when_inherits_from_class_with_flat_id_type() -> None:
    with pytest.raises(MissingEntityIDTypeError):

        class FakeEntityWithFlatIDType(Entity[UUID], namespace=EntityNAMESPACE.TEST):  # pyright: ignore[reportUnusedClass]
            def __init__(self, **kwargs: object) -> None:
                super().__init__(identity_fields=None, **kwargs)


def test_entity_raises_when_inherits_from_class_with_non_uuid_id_type() -> None:
    WrongIDType = NewType("WrongIDType", int)

    with pytest.raises(InvalidEntityIDTypeError):

        class FakeEntityWithWrongIDType(  # pyright: ignore[reportUnusedClass]
            Entity[WrongIDType],  # pyright: ignore[reportInvalidTypeArguments]
            namespace=EntityNAMESPACE.TEST,  # pyright: ignore[reportInvalidTypeArguments]
        ):
            def __init__(self, **kwargs: object) -> None:
                super().__init__(identity_fields=None, **kwargs)


def test_entity_instances_are_immutable() -> None:
    entity = FakeEntity(content="test")

    with pytest.raises(FrozenInstanceError):
        entity.content = "testing..."

    with pytest.raises(FrozenInstanceError):
        del entity.content
