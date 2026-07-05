from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import NewType
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.entity_error import (
    InvalidEntityIDTypeError,
    InvalidIdentityFieldEntityError,
    MissingEntityIDTypeError,
    NonDeterministicValueEntityError,
)
from tests.fakes import TEST, TEST_DIFF, FakeEntity, FakeEntityID

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
    def test_entity_assures_deterministic_content_adressable_id(self) -> None:
        entity_a = FakeEntity(content="test")
        entity_b = FakeEntity(content="test")

        assert entity_a.id == entity_b.id

        assert entity_a == entity_b

        assert len({entity_a, entity_b}) == 1

        assert entity_a is not entity_b

    def test_entity_returns_false_on_comparison_when_namespaces_are_different(
        self,
    ) -> None:
        entity_a = FakeEntity(content="test")
        entity_b = FakeEntityWithDiffNAMESPACE(content="test")

        assert entity_a.id != entity_b.id

        assert entity_a != entity_b

        assert len({entity_a, entity_b}) == 2

    def test_entity_uuid5_uses_only_identity_fields_for_calculation(self) -> None:
        entity_a = FakeEntityWithContentIdentity(content="Alice", extra_field="value_a")
        entity_b = FakeEntityWithContentIdentity(content="Alice", extra_field="value_b")
        entity_c = FakeEntityWithContentIdentity(content="Bob", extra_field="value_a")

        assert entity_a.id == entity_b.id

        assert entity_a.id != entity_c.id

        assert entity_a.extra_field != entity_b.extra_field


class TestEntitySubclassContract:
    def test_entity_preserves_typed_alias_from_injected_id_type(self) -> None:
        assert FakeEntity.id_type.__name__ == FakeEntityID.__name__

        assert callable(FakeEntity.id_type)

        assert isinstance(FakeEntity.id_type(uuid4()), UUID)

    def test_entity_raises_when_inherits_from_class_without_id_type(self) -> None:
        with pytest.raises(MissingEntityIDTypeError):

            class FakeEntityWithoutIDType(Entity, namespace=TEST):  # pyright: ignore[reportUnusedClass, reportMissingTypeArgument]
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(identity_fields=None, **kwargs)

    def test_entity_raises_when_inherits_from_class_with_flat_id_type(self) -> None:
        with pytest.raises(MissingEntityIDTypeError):

            class FakeEntityWithFlatIDType(  # pyright: ignore[reportUnusedClass]
                Entity[UUID], namespace=TEST
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(identity_fields=None, **kwargs)

    def test_entity_raises_when_inherits_from_class_with_non_uuid_id_type(
        self,
    ) -> None:
        WrongIDType = NewType("WrongIDType", int)

        with pytest.raises(InvalidEntityIDTypeError):

            class FakeEntityWithWrongIDType(  # pyright: ignore[reportUnusedClass]
                Entity[WrongIDType],  # pyright: ignore[reportInvalidTypeArguments]
                namespace=TEST,  # pyright: ignore[reportInvalidTypeArguments]
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(identity_fields=None, **kwargs)


class TestEntityValueSemantics:
    def test_entity_is_hashable_inside_of_data_structures(self) -> None:
        entity_a = FakeEntity(content="test_a")
        entity_a_copy = FakeEntity(content="test_a")
        entity_b = FakeEntity(content="test_b")
        entities = {entity_a, entity_b}

        assert hash(entity_a) == hash(entity_a_copy)

        assert hash(entity_a) != hash(entity_b)

        assert entity_a in entities

        assert entity_b in entities

        assert len(entities) == 2

    def test_entity_returns_false_on_comparison_with_diferent_type_object(
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
        id_forward = FakeEntity._calculate_id(content="test", role="admin")  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
        id_reversed = FakeEntity._calculate_id(role="admin", content="test")  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

        assert id_forward == id_reversed

    def test_entity_id_depends_on_values_not_key_names(self) -> None:
        id_content_key = FakeEntity._calculate_id(content="test")  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]
        id_name_key = FakeEntity._calculate_id(name="test")  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

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
    def test_entity_raises_when_identity_value_is_not_a_deterministic_type(
        self, value: object
    ) -> None:
        with pytest.raises(NonDeterministicValueEntityError):
            FakeEntity._calculate_id(content=value)  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]


class TestEntityIdentityFieldsValidation:
    def test_entity_raises_when_identity_field_does_not_exist_in_kwargs(
        self,
    ) -> None:
        with pytest.raises(InvalidIdentityFieldEntityError):
            FakeEntityWithNonexistentIdentityField(
                identity_fields=frozenset({"nonexistent_field"})
            )

    def test_entity_raises_when_identity_fields_contain_nonexistent_attribute_names(
        self,
    ) -> None:
        with pytest.raises(InvalidIdentityFieldEntityError):
            FakeEntityWithNonexistentIdentityField(
                identity_fields=frozenset({"content", "nonexistent_field"}),
                content="test",
            )
