from __future__ import annotations

from decimal import Decimal

import pytest

from osint_engine.infrastructure.errors.data_source_error import (
    UnexpectedFieldTypeError,
    UnexpectedPayloadError,
)
from osint_engine.infrastructure.sources.payload import (
    Payload,
    _runtime_type,  # pyright: ignore[reportPrivateUsage]
)

# TESTS


class TestRuntimeType:
    def test_returns_origin_for_generic_container_types(self) -> None:
        assert _runtime_type(list[int]) is list

    def test_returns_type_unchanged_for_concrete_types(self) -> None:
        assert _runtime_type(str) is str

    def test_returns_union_type_unchanged_so_isinstance_still_works(self) -> None:
        union_type = _runtime_type(int | float)

        assert isinstance(3, union_type)

        assert isinstance(3.0, union_type)

        assert not isinstance("3", union_type)


class TestPayloadRequire:
    def test_raises_when_key_is_missing(self) -> None:
        payload = Payload(source="test", data={})

        with pytest.raises(UnexpectedPayloadError):
            payload.require(key="field", expected_type=str)

    def test_raises_when_field_type_does_not_match_expected_type(self) -> None:
        payload = Payload(source="test", data={"field": 1})

        with pytest.raises(UnexpectedFieldTypeError):
            payload.require(key="field", expected_type=str)

    def test_accepts_union_expected_type(self) -> None:
        payload = Payload(source="test", data={"field": 1.5})

        result = payload.require(
            key="field", expected_type=int | float, cast_to=lambda value: value
        )

        assert result == 1.5

    def test_rejects_value_outside_union_expected_type(self) -> None:
        payload = Payload(source="test", data={"field": "not a number"})

        with pytest.raises(UnexpectedFieldTypeError):
            payload.require(
                key="field", expected_type=int | float, cast_to=lambda value: value
            )

    def test_cast_to_transforms_the_returned_value(self) -> None:
        payload = Payload(source="test", data={"field": 1.5})

        result = payload.require(
            key="field",
            expected_type=int | float,
            cast_to=lambda value: Decimal(str(value)),
        )

        assert result == Decimal("1.5")

    def test_cast_to_is_not_applied_when_type_check_fails(self) -> None:
        payload = Payload(source="test", data={"field": "wrong"})

        with pytest.raises(UnexpectedFieldTypeError):
            payload.require(key="field", expected_type=int, cast_to=Decimal)


class TestPayloadOptional:
    def test_returns_none_when_key_is_absent(self) -> None:
        payload = Payload(source="test", data={})

        result = payload.optional(key="field", expected_type=str)

        assert result is None

    def test_returns_none_when_value_is_null(self) -> None:
        payload = Payload(source="test", data={"field": None})

        result = payload.optional(key="field", expected_type=str)

        assert result is None

    def test_raises_when_present_value_does_not_match_expected_type(self) -> None:
        payload = Payload(source="test", data={"field": 1})

        with pytest.raises(UnexpectedFieldTypeError):
            payload.optional(key="field", expected_type=str)

    def test_accepts_union_expected_type(self) -> None:
        payload = Payload(source="test", data={"field": 1})

        result = payload.optional(
            key="field", expected_type=int | float, cast_to=lambda value: value
        )

        assert result == 1

    def test_cast_to_transforms_the_returned_value(self) -> None:
        payload = Payload(source="test", data={"field": 1})

        result = payload.optional(
            key="field",
            expected_type=int | float,
            cast_to=lambda value: Decimal(str(value)),
        )

        assert result == Decimal("1")

    def test_cast_to_is_not_applied_when_value_is_absent(self) -> None:
        payload = Payload(source="test", data={})

        result = payload.optional(key="field", expected_type=int, cast_to=Decimal)

        assert result is None


class TestPayloadScope:
    def test_scoped_payload_reads_from_narrowed_data(self) -> None:
        payload = Payload(source="test", data={"outer": {"inner": "value"}})
        outer = payload.require(key="outer", expected_type=dict[str, object])

        scoped = payload.scope(data=outer)

        assert scoped.require(key="inner", expected_type=str) == "value"

    def test_scoped_payload_preserves_source_for_error_reporting(self) -> None:
        payload = Payload(source="brasilapi", data={})

        scoped = payload.scope(data={})

        with pytest.raises(UnexpectedPayloadError) as exception:
            scoped.require(key="missing", expected_type=str)

        assert exception.value.source == "brasilapi"

    def test_scope_returns_a_new_independent_instance(self) -> None:
        payload = Payload(source="test", data={"field": "outer"})

        scoped = payload.scope(data={"field": "inner"})

        assert payload.require(key="field", expected_type=str) == "outer"

        assert scoped.require(key="field", expected_type=str) == "inner"
