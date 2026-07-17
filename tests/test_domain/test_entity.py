from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import NewType
from uuid import UUID, uuid4

import pytest

from osint_engine.domain.entities.entity import Entity
from osint_engine.domain.errors.entity_error import (
    EntityEmptyIDFieldNameError,
    EntityInvalidIDFieldError,
    EntityInvalidIDTypeError,
    EntityMissingIDFieldsError,
    EntityMissingIDTypeError,
    EntityNonDeterministicValueError,
)
from tests.fakes.domain import TEST, TEST_DIFF, FakeEntity, FakeEntityID

# TEST DOUBLES


class FakeEntityWithDiffNAMESPACE(
    Entity[FakeEntityID], id_fields=frozenset({"content"}), namespace=TEST_DIFF
):
    content: str

    def __init__(self, *, content: str, **kwargs: object) -> None:
        super().__init__(content=content, **kwargs)


class FakeEntityWithContentIdentity(
    Entity[FakeEntityID], id_fields=frozenset({"content"}), namespace=TEST
):
    content: str
    extra_field: str

    def __init__(
        self,
        *,
        content: str,
        extra_field: str,
        **kwargs: object,
    ) -> None:
        super().__init__(
            content=content,
            extra_field=extra_field,
            **kwargs,
        )


class FakeFakeEntity:
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

    def test_content_id_is_defined(self) -> None:
        entity = FakeEntity(content="test")

        assert hasattr(entity, "content_id")

        assert entity.content_id is not None

    def test_content_id_has_same_type_as_id(self) -> None:
        entity = FakeEntity(content="test")

        assert type(entity.content_id) is type(entity.id)

    def test_content_id_depends_on_all_attributes_not_just_identity_fields(
        self,
    ) -> None:
        entity_a = FakeEntityWithContentIdentity(content="Alice", extra_field="value_a")
        entity_b = FakeEntityWithContentIdentity(content="Alice", extra_field="value_b")

        assert entity_a.id == entity_b.id

        assert entity_a.content_id != entity_b.content_id

    def test_set_deduplicates_entities_by_id_not_content_id(self) -> None:
        entity_a = FakeEntityWithContentIdentity(content="Alice", extra_field="value_a")
        entity_b = FakeEntityWithContentIdentity(content="Alice", extra_field="value_b")

        assert entity_a.id == entity_b.id

        assert entity_a.content_id != entity_b.content_id

        assert len({entity_a, entity_b}) == 1


class TestEntitySubclassContract:
    def test_id_type_is_bound_to_subclass(self) -> None:
        assert FakeEntity.id_type.__name__ == FakeEntityID.__name__

        assert callable(FakeEntity.id_type)

        assert isinstance(FakeEntity.id_type(uuid4()), UUID)

    def test_raises_without_id_type_parameter(self) -> None:
        with pytest.raises(EntityMissingIDTypeError) as exception:

            class FakeEntityWithoutIDType(  # pyright: ignore[reportUnusedClass]
                Entity,  # pyright: ignore[reportMissingTypeArgument]
                id_fields=frozenset({"content"}),
                namespace=TEST,
            ):
                content: str

                def __init__(self, *, content: str, **kwargs: object) -> None:
                    super().__init__(content=content, **kwargs)

        assert "FakeEntityWithoutIDType" in str(exception.value)

    def test_raises_with_plain_uuid_as_id_type(self) -> None:
        with pytest.raises(EntityMissingIDTypeError) as exception:

            class FakeEntityWithFlatIDType(  # pyright: ignore[reportUnusedClass]
                Entity[UUID], id_fields=frozenset({"content"}), namespace=TEST
            ):
                content: str

                def __init__(self, content: str, **kwargs: object) -> None:
                    super().__init__(content=content, **kwargs)

        assert "FakeEntityWithFlatIDType" in str(exception.value)

    def test_raises_with_non_uuid_id_type(
        self,
    ) -> None:
        WrongIDType = NewType("WrongIDType", int)

        with pytest.raises(EntityInvalidIDTypeError) as exception:

            class FakeEntityWithWrongIDType(  # pyright: ignore[reportUnusedClass]
                Entity[WrongIDType],  # pyright: ignore[reportInvalidTypeArguments]
                id_fields=frozenset({"content"}),
                namespace=TEST,
            ):
                content: str

                def __init__(self, content: str, **kwargs: object) -> None:
                    super().__init__(content=content, **kwargs)

        assert "WrongIDType" in str(exception.value)

        assert "FakeEntityWithWrongIDType" in str(exception.value)


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

    def test_entity_id_depends_on_key_names_not_just_values(self) -> None:
        id_content_key = FakeEntity._calculate_id(content="test")  # pyright: ignore[reportPrivateUsage]
        id_name_key = FakeEntity._calculate_id(name="test")  # pyright: ignore[reportPrivateUsage]

        assert id_content_key != id_name_key

    def test_entity_id_is_stable_for_same_key_name_and_value(self) -> None:
        id_a = FakeEntity._calculate_id(content="test")  # pyright: ignore[reportPrivateUsage]
        id_b = FakeEntity._calculate_id(content="test")  # pyright: ignore[reportPrivateUsage]

        assert id_a == id_b

    @pytest.mark.parametrize(
        "value",
        [
            pytest.param(["a", "b"], id="list"),
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
        with pytest.raises(EntityNonDeterministicValueError) as exception:
            FakeEntity._calculate_id(content=value)  # pyright: ignore[reportPrivateUsage]

        assert type(value).__name__ in str(exception.value)


class TestEntityIdentityFieldsValidation:
    def test_raises_when_identity_field_is_absent_from_kwargs(
        self,
    ) -> None:
        with pytest.raises(EntityInvalidIDFieldError) as exception:

            class _FakeEntity(  # pyright: ignore[reportUnusedClass]
                Entity[FakeEntityID],
                id_fields=frozenset({"nonexistent_field"}),
                namespace=TEST,
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

        assert "nonexistent_field" in str(exception.value)

    def test_raises_when_any_identity_field_is_unknown(
        self,
    ) -> None:
        with pytest.raises(EntityInvalidIDFieldError) as exception:

            class _FakeEntity(  # pyright: ignore[reportUnusedClass]
                Entity[FakeEntityID],
                id_fields=frozenset({"content", "nonexistent_field"}),
                namespace=TEST,
            ):
                content: str

                def __init__(self, *, content: str, **kwargs: object) -> None:
                    super().__init__(content=content, **kwargs)

        assert "nonexistent_field" in str(exception.value)

    def test_raises_when_identity_field_name_is_empty_string(
        self,
    ) -> None:
        with pytest.raises(EntityEmptyIDFieldNameError) as exception:

            class _FakeEntity(  # pyright: ignore[reportUnusedClass]
                Entity[FakeEntityID], id_fields=frozenset({""}), namespace=TEST
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

        assert "FakeEntity" in str(exception.value)

    def test_raises_when_id_fields_is_none_on_a_concrete_entity(self) -> None:
        with pytest.raises(EntityMissingIDFieldsError) as exception:

            class _FakeEntity(  # pyright: ignore[reportUnusedClass]
                Entity[FakeEntityID], id_fields=None, namespace=TEST
            ):
                def __init__(self, **kwargs: object) -> None:
                    super().__init__(**kwargs)

        assert "_FakeEntity" in str(exception.value)


class TestEntityReconstructKwargs:
    def test_returns_declared_init_fields_with_their_current_values(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="value")

        assert entity.reconstruct_kwargs() == {
            "content": "Alice",
            "extra_field": "value",
        }

    def test_excludes_self_and_var_keyword_parameters(self) -> None:
        kwargs = FakeEntityWithContentIdentity(
            content="Alice", extra_field="value"
        ).reconstruct_kwargs()

        assert "self" not in kwargs

        assert "kwargs" not in kwargs

    def test_round_trips_through_the_constructor(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="value")

        rebuilt = type(entity)(**entity.reconstruct_kwargs())  # pyright: ignore[reportArgumentType]

        assert rebuilt == entity

        assert rebuilt.content_id == entity.content_id


class TestEntityEvolve:
    def test_preserves_unspecified_fields(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="original")

        evolved = entity.evolve(extra_field="changed")

        assert evolved.content == "Alice"

        assert evolved.extra_field == "changed"

    def test_returns_a_new_instance_of_the_same_type(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="value")

        evolved = entity.evolve(extra_field="other")

        assert type(evolved) is type(entity)

        assert evolved is not entity

    def test_with_no_changes_reproduces_an_identical_entity(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="value")

        evolved = entity.evolve()

        assert evolved == entity

        assert evolved.content_id == entity.content_id

    def test_changing_a_non_identity_field_keeps_id_but_shifts_content_id(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="value")

        evolved = entity.evolve(extra_field="other")

        assert evolved.id == entity.id

        assert evolved.content_id != entity.content_id

    def test_changing_an_identity_field_recomputes_id(self) -> None:
        entity = FakeEntityWithContentIdentity(content="Alice", extra_field="value")

        evolved = entity.evolve(content="Bob")

        assert evolved.id != entity.id
