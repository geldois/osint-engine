from __future__ import annotations

from typing import cast, get_origin

from osint_engine.infrastructure.errors.fetcher_error import (
    UnexpectedFieldTypeFetcherError,
    UnexpectedSchemaFetcherError,
)


def _runtime_type(tp: type) -> type:
    return get_origin(tp) or tp


class Schema:
    def __init__(self, *, source: str, data: dict[str, object]) -> None:
        self._source = source
        self._data = data

    def has_key(self, key: str, /) -> bool:
        return self._data.get(key) is not None

    def require[Field: object](
        self,
        *,
        key: str,
        exp_type: type[Field],
        ext_data: dict[str, object] | None = None,
    ) -> Field:
        data = ext_data if ext_data is not None else self._data

        if key not in data:
            raise UnexpectedSchemaFetcherError(source=self._source, missing_field=key)

        field = data[key]

        if not isinstance(field, _runtime_type(exp_type)):
            raise UnexpectedFieldTypeFetcherError(
                source=self._source,
                key=key,
                expected_type=exp_type,
                field_type=type(field),
            )

        return cast("Field", field)

    def optional[Field: object](
        self,
        *,
        key: str,
        exp_type: type[Field],
        ext_data: dict[str, object] | None = None,
    ) -> Field | None:
        data = ext_data if ext_data is not None else self._data

        if key not in data:
            return None

        field = data[key]

        if field is None or not isinstance(field, _runtime_type(exp_type)):
            return None

        return cast("Field", field)
