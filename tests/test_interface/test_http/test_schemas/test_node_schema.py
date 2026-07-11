from __future__ import annotations

from inspect import isabstract
from typing import TYPE_CHECKING, Literal, override

import pytest

from osint_engine.interface.http.errors.schema_error import (
    DuplicateSchemaRegistrationError,
    MissingDiscriminatorFieldError,
    UnmappedTypeSchemaError,
)
from osint_engine.interface.http.schemas.node_schema import (
    NodeSchema,
    NodeSchemaRegistry,
)
from tests.fakes.domain import FakeNode

if TYPE_CHECKING:
    from uuid import UUID

    from osint_engine.domain.entities.bases.node import Node


def _concrete_node_schemas() -> list[type[NodeSchema[Node[UUID]]]]:
    result: list[type[NodeSchema[Node[UUID]]]] = []

    def _walk(*, base: type) -> None:
        for cls in base.__subclasses__():
            if not isabstract(cls) and cls.__module__.startswith("osint_engine"):
                result.append(cls)

            _walk(base=cls)

    _walk(base=NodeSchema)

    return result


# TEST DOUBLES


class ValidFakeNodeSchema(NodeSchema[FakeNode]):
    type: Literal["fake_node"] = "fake_node"

    @classmethod
    @override
    def domain(cls) -> type[FakeNode]:
        return FakeNode


# TESTS


class TestNodeSchemaContractEnforcement:
    def test_raises_when_type_field_is_absent(self) -> None:
        with pytest.raises(MissingDiscriminatorFieldError) as exception:

            class MissingTypeSchema(NodeSchema[FakeNode]):  # pyright: ignore[reportUnusedClass]
                @classmethod
                @override
                def domain(cls) -> type[FakeNode]:
                    return FakeNode

        assert "MissingTypeSchema" in str(exception.value)

    def test_raises_when_type_is_plain_string(self) -> None:
        with pytest.raises(MissingDiscriminatorFieldError) as exception:

            class FlatStringTypeSchema(NodeSchema[FakeNode]):  # pyright: ignore[reportUnusedClass]
                type: str = "fake_node"

                @classmethod
                @override
                def domain(cls) -> type[FakeNode]:
                    return FakeNode

        assert "FlatStringTypeSchema" in str(exception.value)


class TestNodeSchemaDomainClassmethod:
    def test_domain_returns_exact_node_type(self) -> None:
        assert ValidFakeNodeSchema.domain() is FakeNode


class TestNodeSchemaRegistryLookup:
    @pytest.mark.parametrize("schema_class", _concrete_node_schemas())
    def test_every_concrete_schema_is_registered(
        self, schema_class: type[NodeSchema[Node[UUID]]]
    ) -> None:
        domain = schema_class.domain()

        assert NodeSchemaRegistry.get_from_domain(domain) is schema_class


class TestNodeSchemaRegistryErrors:
    def test_raises_for_unmapped_domain_type(self) -> None:
        class UnknownNode: ...  # pyright: ignore[reportUnusedClass]

        with pytest.raises(UnmappedTypeSchemaError) as exception:
            NodeSchemaRegistry.get_from_domain(UnknownNode)  # pyright: ignore[reportArgumentType]

        assert "UnknownNode" in str(exception.value)


class TestNodeSchemaRegistryRegister:
    def test_register_maps_schema_to_domain_key(self) -> None:
        NodeSchemaRegistry.register(ValidFakeNodeSchema)

        assert NodeSchemaRegistry.get_from_domain(FakeNode) is ValidFakeNodeSchema

    def test_raises_for_duplicate_registration(self) -> None:
        with pytest.raises(DuplicateSchemaRegistrationError) as exception:
            NodeSchemaRegistry.register(ValidFakeNodeSchema)

        assert "ValidFakeNodeSchema" in str(exception.value)
