from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import NewType
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.entity_error import (
    EntityInvalidIdentityFieldError,
    EntityInvalidIDTypeError,
    EntityMissingIDTypeError,
    EntityNonDeterministicValueError,
)
from tests.fakes.domain import TEST, TEST_DIFF, FakeEntity, FakeEntityID

# TEST DOUBLES


class FakeEntityWithDiffNAMESPACE(Entity[FakeEntityID], namespace=TEST_DIFF):
    content: str

    def __init__(
        self,
        *,
        identity_fields: frozenset[str] | None = None,
        content: str,
        **kwargs: object,
    ) -> None:
        super().__init__(identity_fields=identity_fields, content=content, **kwargs)


class FakeEntityWithNonexistentIdentityField(Entity[FakeEntityID], namespace=TEST):
    def __init__(
        self, *, identity_fields: frozenset[str] | None, **kwargs: object
    ) -> None:
        super().__init__(
            identity_fields=identity_fields,
            **kwargs,
        )


class FakeEntityWithContentIdentity(Entity[FakeEntityID], namespace=TEST):
    content: str
    extra_field: str

    def __init__(
        self,
        *,
        identity_fields: frozenset[str] | None = frozenset({"content"}),
        content: str,
        extra_field: str,
        **kwargs: object,
    ) -> None:
        super().__init__(
            identity_fields=identity_fields,
            content=content,
            extra_field=extra_field,
            **kwargs,
        )


class FakeFakeEntity:  # Not an Entity — sentinel for type-mismatch tests
    def __init__(self, *, content: str) -> None:
        self.id = uuid4()
        self.content = content


# TESTS


class TestEntityIdentity:
    def test_equal_content_produces_equal_entities(self) -> None:
        entity_a = FakeEntity(content="test")
        entity_b = FakeEntity(content="test")

        assert entity_a.id == entity_b.id

        assert entity_a == entity_b

        assert len({entity_a, entity_b}) == 1

        assert entity_a is not entity_b

    def test_different_namespace_produces_different_id(
        self,
    ) -> None:
        entity_a = FakeEntity(content="test")
        entity_b = FakeEntityWithDiffNAMESPACE(content="test")

        assert entity_a.id != entity_b.id

        assert entity_a != entity_b

        assert len({entity_a, entity_b}) == 2

    def test_id_depends_only_on_identity_fields(self) -> None:
        entity_a = FakeEntityWithContentIdentity(content="Alice", extra_field="value_a")
        entity_b = FakeEntityWithContentIdentity(content="Alice", extra_field="value_b")
        entity_c = FakeEntityWithContentIdentity(content="Bob", extra_field="value_a")

        assert entity_a.id == entity_b.id

        assert entity_a.id != entity_c.id

        assert entity_a.extra_field != entity_b.extra_field


class TestEntitySubclassContract:
    def test_id_type_is_bound_to_subclass(self) -> None:
        assert FakeEntity.id_type.__name__ == FakeEntityID.__name__

        assert callable(FakeEntity.id_type)

        assert isinstance(FakeEntity.id_type(uuid4()), UUID)

    def test_raises_without_id_type_parameter(self) -> None:
        with pytest.raises(EntityMissingIDTypeError):

            class FakeEntityWithoutIDType(Entity, namespace=TEST):  # pyright: ignore[reportUnusedClass, reportMissingTypeArgument]
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(identity_fields=None, **kwargs)

    def test_raises_with_plain_uuid_as_id_type(self) -> None:
        with pytest.raises(EntityMissingIDTypeError):

            class FakeEntityWithFlatIDType(  # pyright: ignore[reportUnusedClass]
                Entity[UUID], namespace=TEST
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(identity_fields=None, **kwargs)

    def test_raises_with_non_uuid_id_type(
        self,
    ) -> None:
        WrongIDType = NewType("WrongIDType", int)

        with pytest.raises(EntityInvalidIDTypeError):

            class FakeEntityWithWrongIDType(  # pyright: ignore[reportUnusedClass]
                Entity[WrongIDType],  # pyright: ignore[reportInvalidTypeArguments]
                namespace=TEST,
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(identity_fields=None, **kwargs)


class TestEntityValueSemantics:
    def test_entity_is_hashable(self) -> None:
        entity_a = FakeEntity(content="test_a")
        entity_a_copy = FakeEntity(content="test_a")
        entity_b = FakeEntity(content="test_b")
        entities = {entity_a, entity_b}

        assert hash(entity_a) == hash(entity_a_copy)

        assert hash(entity_a) != hash(entity_b)

        assert entity_a in entities

        assert entity_b in entities

        assert len(entities) == 2

    def test_entity_is_not_equal_to_foreign_type(
        self,
    ) -> None:
        entity_a = FakeEntity(content="test")
        entity_b = FakeFakeEntity(content="test")

        assert entity_a != entity_b

    def test_entity_instances_are_immutable(self) -> None:
        entity = FakeEntity(content="test")

        with pytest.raises(FrozenInstanceError):
            entity.content = "testing..."

        with pytest.raises(FrozenInstanceError):
            del entity.content


class TestEntityIDCalculation:
    def test_entity_id_is_stable_under_kwarg_order(self) -> None:
        id_forward = FakeEntity._calculate_id(content="test", role="admin")  # pyright: ignore[reportPrivateUsage]
        id_reversed = FakeEntity._calculate_id(role="admin", content="test")  # pyright: ignore[reportPrivateUsage]

        assert id_forward == id_reversed

    def test_entity_id_depends_on_values_not_key_names(self) -> None:
        id_content_key = FakeEntity._calculate_id(content="test")  # pyright: ignore[reportPrivateUsage]
        id_name_key = FakeEntity._calculate_id(name="test")  # pyright: ignore[reportPrivateUsage]

        assert id_content_key == id_name_key

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(["a", "b"], id="list"),
            pytest.param(("a", "b"), id="tuple"),
            pytest.param({"key": "value"}, id="dict"),
            pytest.param({"a", "b"}, id="set"),
            pytest.param(1.0, id="float"),
            pytest.param(b"bytes", id="bytes"),
            pytest.param(object(), id="arbitrary_object"),
        ],
    )
    def test_raises_when_identity_value_is_not_deterministic(
        self, value: object
    ) -> None:
        with pytest.raises(EntityNonDeterministicValueError):
            FakeEntity._calculate_id(content=value)  # pyright: ignore[reportPrivateUsage]


class TestEntityIdentityFieldsValidation:
    def test_raises_when_identity_field_is_absent_from_kwargs(
        self,
    ) -> None:
        with pytest.raises(EntityInvalidIdentityFieldError):
            FakeEntityWithNonexistentIdentityField(
                identity_fields=frozenset({"nonexistent_field"})
            )

    def test_raises_when_any_identity_field_is_unknown(
        self,
    ) -> None:
        with pytest.raises(EntityInvalidIdentityFieldError):
            FakeEntityWithNonexistentIdentityField(
                identity_fields=frozenset({"content", "nonexistent_field"}),
                content="test",
            )
