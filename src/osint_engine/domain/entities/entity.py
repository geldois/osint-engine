from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal
from inspect import isabstract
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeGuard,
    TypeVar,
    final,
    get_args,
    get_origin,
)
from uuid import UUID, uuid4, uuid5

from osint_engine.domain.errors.entity_error import (
    EntityEmptyIdentityFieldNameError,
    EntityInvalidIdentityFieldError,
    EntityInvalidIDTypeError,
    EntityMissingIDTypeError,
    EntityNonDeterministicValueError,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from osint_engine.domain.value_objects.entity_namespace import EntityNAMESPACE


IDType_co = TypeVar("IDType_co", bound=UUID, covariant=True)


_DETERMINISTIC_TYPES: tuple[type, ...] = (
    bool,
    datetime,
    Decimal,
    int,
    str,
    tuple,
    type(None),
    UUID,
)


def _is_tuple(*, value: object) -> TypeGuard[tuple[object, ...]]:
    return isinstance(value, tuple)


def _validate_deterministic_type(*, value: object) -> None:
    if type(value) not in _DETERMINISTIC_TYPES:
        raise EntityNonDeterministicValueError(value=value)

    if _is_tuple(value=value):
        for v in value:
            _validate_deterministic_type(value=v)


def _validate_entity_id_type[IDType: UUID](*, subject: type[Entity[IDType]]) -> None:
    if not hasattr(subject, "id_type") and not isabstract(subject):
        raise EntityMissingIDTypeError(subject=subject)


def _validate_identity_fields(
    *, identity_fields: frozenset[str], subject: type, valid_fields: dict[str, object]
) -> None:
    for field in identity_fields:
        if not field:
            raise EntityEmptyIdentityFieldNameError(subject=subject)

        if field not in valid_fields:
            raise EntityInvalidIdentityFieldError(
                field=field, subject=subject, valid_fields=valid_fields
            )


class Entity(ABC, Generic[IDType_co]):  # noqa: UP046
    content_id: IDType_co
    id: IDType_co

    @final
    def __init_subclass__(cls, *, namespace: EntityNAMESPACE, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

        cls.namespace = namespace.namespace

        for base in getattr(cls, "__orig_bases__", ()):
            origin = get_origin(base)

            if origin is None:
                continue

            if not (isinstance(origin, type) and issubclass(origin, Entity)):
                continue

            args = get_args(base)

            if not args:
                continue

            candidate = args[0]

            if not hasattr(candidate, "__supertype__"):
                continue

            if not issubclass(candidate.__supertype__, UUID):
                raise EntityInvalidIDTypeError(subject=cls, id_type=candidate)

            probe = candidate(uuid4())

            if not isinstance(probe, UUID):
                raise EntityInvalidIDTypeError(subject=cls, id_type=candidate)

            cls.id_type: Callable[[UUID], IDType_co] = staticmethod(candidate)

        _validate_entity_id_type(subject=cls)

    @abstractmethod
    def __init__(self, *, identity_fields: frozenset[str], **kwargs: object) -> None:
        object.__setattr__(self, "content_id", self._calculate_id(**kwargs))

        _validate_identity_fields(
            identity_fields=identity_fields, subject=type(self), valid_fields=kwargs
        )

        identified_by = {field: kwargs[field] for field in identity_fields}

        object.__setattr__(self, "id", self._calculate_id(**identified_by))

        for k, v in kwargs.items():
            object.__setattr__(self, k, v)

    @final
    def __setattr__(self, name: str, value: object, /) -> None:
        raise FrozenInstanceError

    @final
    def __delattr__(self, name: str, /) -> None:
        raise FrozenInstanceError

    @final
    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.id == other.id

    @final
    def __hash__(self) -> int:
        return self.id.int

    @classmethod
    def _calculate_id(cls, **kwargs: object) -> IDType_co:
        parameter_pairs: list[tuple[str, object]] = []

        for parameter_name, parameter in kwargs.items():
            _validate_deterministic_type(value=parameter)

            parameter_pairs.append((parameter_name, parameter))

        parameter_pairs.sort(key=lambda pair: (pair[0], str(pair[1])))

        return cls.id_type(
            uuid5(
                namespace=cls.namespace, name=json.dumps(parameter_pairs, default=str)
            )
        )
