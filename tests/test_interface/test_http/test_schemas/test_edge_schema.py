from __future__ import annotations

from inspect import isabstract
from typing import TYPE_CHECKING, Literal, override

import pytest

from osint_engine.interface.http.errors.schema_error import (
    DuplicateSchemaRegistrationError,
    MissingDiscriminatorFieldError,
    UnmappedTypeSchemaError,
)
from osint_engine.interface.http.schemas.edge_schema import (
    EdgeSchema,
    EdgeSchemaRegistry,
)
from tests.fakes.domain import FakeEdge

if TYPE_CHECKING:
    from collections.abc import Iterator
    from uuid import UUID

    from osint_engine.domain.entities.bases.edge import Edge


def _concrete_edge_schemas() -> list[type[EdgeSchema[Edge[UUID, UUID, UUID]]]]:
    result: list[type[EdgeSchema[Edge[UUID, UUID, UUID]]]] = []

    def _walk(*, base: type) -> None:
        for cls in base.__subclasses__():
            if not isabstract(cls) and cls.__module__.startswith("osint_engine"):
                result.append(cls)

            _walk(base=cls)

    _walk(base=EdgeSchema)

    return result


# TEST DOUBLES


class ValidFakeEdgeSchema(EdgeSchema[FakeEdge]):
    type: Literal["fake_edge"] = "fake_edge"

    @classmethod
    @override
    def domain(cls) -> type[FakeEdge]:
        return FakeEdge


# TESTS


class TestEdgeSchemaContractEnforcement:
    def test_raises_when_type_field_is_absent(self) -> None:
        with pytest.raises(MissingDiscriminatorFieldError) as exception:

            class MissingTypeSchema(EdgeSchema[FakeEdge]):  # pyright: ignore[reportUnusedClass]
                @classmethod
                @override
                def domain(cls) -> type[FakeEdge]:
                    return FakeEdge

        assert "MissingTypeSchema" in str(exception.value)

    def test_raises_when_type_is_plain_string(self) -> None:
        with pytest.raises(MissingDiscriminatorFieldError) as exception:

            class FlatStringTypeSchema(EdgeSchema[FakeEdge]):  # pyright: ignore[reportUnusedClass]
                type: str = "fake_edge"

                @classmethod
                @override
                def domain(cls) -> type[FakeEdge]:
                    return FakeEdge

        assert "FlatStringTypeSchema" in str(exception.value)


class TestEdgeSchemaDomainClassmethod:
    def test_domain_returns_exact_edge_type(self) -> None:
        assert ValidFakeEdgeSchema.domain() is FakeEdge


class TestEdgeSchemaRegistryLookup:
    @pytest.mark.parametrize("schema_class", _concrete_edge_schemas())
    def test_every_concrete_schema_is_registered(
        self, schema_class: type[EdgeSchema[Edge[UUID, UUID, UUID]]]
    ) -> None:
        domain = schema_class.domain()

        assert EdgeSchemaRegistry.get_from_domain(domain) is schema_class


class TestEdgeSchemaRegistryErrors:
    def test_raises_for_unmapped_domain_type(self) -> None:
        class UnknownEdge: ...  # pyright: ignore[reportUnusedClass]

        with pytest.raises(UnmappedTypeSchemaError) as exception:
            EdgeSchemaRegistry.get_from_domain(UnknownEdge)  # pyright: ignore[reportArgumentType]

        assert "UnknownEdge" in str(exception.value)


class TestEdgeSchemaRegistryRegister:
    @pytest.fixture(autouse=True)
    def _unregister_fake_edge(self) -> Iterator[None]:
        yield

        EdgeSchemaRegistry._REGISTRY.pop(FakeEdge, None)  # pyright: ignore[reportPrivateUsage]

    def test_register_maps_schema_to_domain_key(self) -> None:
        EdgeSchemaRegistry.register(ValidFakeEdgeSchema)

        assert EdgeSchemaRegistry.get_from_domain(FakeEdge) is ValidFakeEdgeSchema

    def test_raises_for_duplicate_registration(self) -> None:
        EdgeSchemaRegistry.register(ValidFakeEdgeSchema)

        with pytest.raises(DuplicateSchemaRegistrationError) as exception:
            EdgeSchemaRegistry.register(ValidFakeEdgeSchema)

        assert "ValidFakeEdgeSchema" in str(exception.value)
