from __future__ import annotations

from collections.abc import Callable
from types import UnionType
from typing import Union, cast, get_origin, overload

from osint_engine.infrastructure.errors.provider_error import (
    UnexpectedFieldTypeError,
    UnexpectedPayloadError,
)

type _Caster[Field, Cast] = Callable[[Field], Cast]


def _runtime_type(type_: type | UnionType, /) -> type | UnionType:
    origin = get_origin(type_)

    if origin is Union or origin is UnionType:
        return type_

    return origin or type_


class Payload:
    def __init__(self, *, provider: str, data: dict[str, object]) -> None:
        self._provider = provider
        self._data = data

    @property
    def provider(self) -> str:
        return self._provider

    def scope(self, *, data: dict[str, object]) -> Payload:
        cls = type(self)

        return cls(provider=self._provider, data=data)

    @overload
    def require[Field: object](
        self, *, key: str, expected_type: type[Field], cast_to: None = None
    ) -> Field: ...

    @overload
    def require[Field: object, Cast: object](
        self, *, key: str, expected_type: type[Field], cast_to: _Caster[Field, Cast]
    ) -> Cast: ...

    def require[Field: object, Cast: object](
        self,
        *,
        key: str,
        expected_type: type[Field],
        cast_to: _Caster[Field, Cast] | None = None,
    ) -> Field | Cast:

        if key not in self._data:
            raise UnexpectedPayloadError(provider=self._provider, missing_field=key)

        field = self._data[key]

        if not isinstance(field, _runtime_type(expected_type)):
            raise UnexpectedFieldTypeError(
                provider=self._provider,
                key=key,
                expected_type=expected_type,
                field_type=type(field),
            )

        field = cast("Field", field)

        return cast_to(field) if cast_to is not None else field

    @overload
    def optional[Field: object](
        self, *, key: str, expected_type: type[Field], cast_to: None = None
    ) -> Field | None: ...

    @overload
    def optional[Field: object, Cast: object](
        self, *, key: str, expected_type: type[Field], cast_to: _Caster[Field, Cast]
    ) -> Cast | None: ...

    def optional[Field: object, Cast: object](
        self,
        *,
        key: str,
        expected_type: type[Field],
        cast_to: _Caster[Field, Cast] | None = None,
    ) -> Field | Cast | None:

        if key not in self._data or self._data[key] is None:
            return None

        field = self._data[key]

        if not isinstance(field, _runtime_type(expected_type)):
            raise UnexpectedFieldTypeError(
                provider=self._provider,
                key=key,
                expected_type=expected_type,
                field_type=type(field),
            )

        field = cast("Field", field)

        return cast_to(field) if cast_to is not None else field
